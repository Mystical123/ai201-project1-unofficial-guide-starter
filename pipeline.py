import os
import re

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

def chunk_text(text, source, chunk_size=500, overlap=100):
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

if __name__ == "__main__":
    documents = load_documents()
    print(f"\nTotal documents loaded: {len(documents)}")

    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"], doc["source"])
        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")

    # print 5 sample chunks to inspect
    print("\n--- Sample chunks ---")
    import random
    for chunk in random.sample(all_chunks, 5):
        print(f"\n[Source: {chunk['source']}]")
        print(chunk["text"])
        print("-" * 40)
