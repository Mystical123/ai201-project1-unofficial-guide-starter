import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# these are module-level so they load once and stay in memory
_model = None
_collection = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_collection():
    global _collection
    if _collection is None:
        from pipeline import load_documents, chunk_text
        documents = load_documents()
        all_chunks = []
        for doc in documents:
            chunks = chunk_text(doc["text"], doc["source"])
            all_chunks.extend(chunks)

        model = get_model()
        client = chromadb.Client()
        collection = client.create_collection(
            name="professor_reviews",
            metadata={"hnsw:space": "cosine"}
        )

        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = model.encode(texts)
        collection.add(
            ids=[str(i) for i in range(len(all_chunks))],
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[{"source": chunk["source"], "chunk_index": i} for i, chunk in enumerate(all_chunks)]
        )
        _collection = collection
    return _collection


def retrieve(query, top_k=5):
    model = get_model()
    collection = get_collection()
    query_embedding = model.encode([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({
            "text": doc,
            "source": meta["source"]
        })
    return chunks


def ask(question):
    chunks = retrieve(question)

    context = ""
    for i, chunk in enumerate(chunks):
        context += f"[Source: {chunk['source']}]\n{chunk['text']}\n\n"

    system_prompt = """You are a helpful assistant that answers questions about CS professors at Sacramento State University.
Answer ONLY using the information provided in the context below.
Do not use any outside knowledge or general assumptions.
Always cite which source document(s) your answer comes from.
If the context does not contain enough information to answer the question, say exactly: 'I don't have enough information on that.'"""

    user_prompt = f"""Context:
{context}

Question: {question}

Answer based only on the context above. At the end of your answer, list the sources you used."""

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content
    sources = list(set(chunk["source"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":
    test_questions = [
        "Which professor has the most useful lectures?",
        "Which professor has the easiest exams?",
        "What is the best restaurant near campus?"  # out of scope test
    ]

    for q in test_questions:
        print(f"\n{'='*50}")
        print(f"Question: {q}")
        print('='*50)
        result = ask(q)
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources'])}")
