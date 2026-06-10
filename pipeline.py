import os
import re
import random
from sentence_transformers import SentenceTransformer
import chromadb

DOCUMENTS_DIR = "documents"

NOISE_PATTERNS = [
    r"Rate\n",
    r"Compare\n",
    r"Arrow Icon\n",
    r"Jump To Ratings Down Arrow\n",
    r"Thumbs up\n",
    r"Thumbs down\n",
    r"I'm Professor \w+\n",
    r"Rating Distribution\n",
    r"Awesome 5\n",
    r"Great 4\n",
    r"Good 3\n",
    r"OK 2\n",
    r"Awful 1\n",
    r"Overall Quality Based on \d+ ratings\n",
    r"Professor in the .+ department at .+\n",
    r"Similar Professors[\s\S]+?(?=\n\n|\Z)",  # entire "Similar Professors" block
    r"\d{2}:\d{2}\n/\n\d{2}:\d{2}",           # timestamp block like 00:00 / 00:00
    r"\d{2}:\d{2}",                            # any remaining standalone timestamp
    r"\d+ Student Ratings\n",                  # "20 Student Ratings"
    r"All courses\n",
    r"^/ 5$",                                  # aggregate rating denominator
    r"^/$",                                    # standalone slash left from timestamp removal
    r"^\d+\.\d+$",                             # standalone decimals like 3.9, 4.4 (aggregate ratings)
    r"^\d{2,}$",                               # standalone integers with 2+ digits like 10, 107 (counts)
    r"^[0-9]$",                                # single digit standalone numbers

]

def clean_text(text):
    # merge label+value pairs onto one line BEFORE removing standalone numbers
    text = re.sub(r"(Quality|Difficulty)\n(\d+\.?\d*)", r"\1: \2", text)

    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.MULTILINE)

    # collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # strip leading/trailing whitespace
    text = text.strip()

    return text

def load_documents():
    documents = []

    for filename in os.listdir(DOCUMENTS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCUMENTS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned_text = clean_text(raw_text)
            documents.append({
                "source": filename,
                "text": cleaned_text
            })
            print(f"Loaded: {filename} ({len(cleaned_text)} chars)")

    return documents

def chunk_text(text, source, chunk_size=800, overlap=150):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if len(chunk) > 0:
            chunks.append({
                "source": source,
                "text": chunk
            })

        start += chunk_size - overlap

    return chunks

def embed_and_store(chunks):
    print("\nLoading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.Client()
    collection = client.create_collection(
        name="professor_reviews",
        metadata={"hnsw:space": "cosine"}
    )

    print(f"Embedding and storing {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[{"source": chunk["source"], "chunk_index": i} for i, chunk in enumerate(chunks)]
    )

    print(f"Stored {collection.count()} chunks in ChromaDB")
    return collection, model


def retrieve(query, collection, model, top_k=5):
    query_embedding = model.encode([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    return results


if __name__ == "__main__":
    documents = load_documents()
    print(f"\nTotal documents loaded: {len(documents)}")

    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"], doc["source"])
        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")

    collection, model = embed_and_store(all_chunks)

    # test retrieval with 3 evaluation queries
    test_queries = [
        "Which professor has the most useful lectures?",
        "Which professor has the easiest exams?",
        "Which professor responds fastest to emails?"
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        results = retrieve(query, collection, model)
        for i, (doc, meta, distance) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            print(f"\n[Result {i+1}] Source: {meta['source']} | Distance: {distance:.3f}")
            print(doc[:300])
