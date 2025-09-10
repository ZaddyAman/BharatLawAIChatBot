import os
import re
import asyncio
import functools
from uuid import uuid4
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

# ChromaDB setup
DB_DIR = "./chroma_db"
client = PersistentClient(path=DB_DIR)
collection_name = "legal_assistant"

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create collection (or get if it exists)
collection = client.get_or_create_collection(collection_name)

# 🔍 Pattern to detect section blocks like "Section 246. Title"
section_pattern = re.compile(r"(Section\s+\d+\.\s.*?)(?=Section\s+\d+\.|\Z)", re.DOTALL | re.IGNORECASE)

# 📁 Data directory
DATA_DIR = "./data"

def extract_act_from_filename(filename: str) -> str:
    base = os.path.basename(filename).lower()
    if "ipc" in base:
        return "IPC"
    elif "crpc" in base:
        return "CrPC"
    return "Unknown"

def extract_section_no(section_text: str) -> str:
    match = re.match(r"(Section\s+\d+\.)", section_text.strip(), re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown"

async def embed_and_store(filepath: str):
    loop = asyncio.get_event_loop()

    # Read file asynchronously
    content = await loop.run_in_executor(None, functools.partial(open, filepath, "r", encoding="utf-8"))
    with content as f:
        file_content = await loop.run_in_executor(None, f.read)

    sections = section_pattern.findall(file_content)
    act = extract_act_from_filename(filepath)
    print(f"📖 Processing {len(sections)} sections from {act} ({filepath})")

    for section_text in sections:
        section_no = extract_section_no(section_text)
        doc_id = str(uuid4())
        
        # Encode embedding asynchronously
        embedding = await loop.run_in_executor(None, functools.partial(model.encode, section_text))
        embedding = embedding.tolist()

        # Add to collection asynchronously
        await loop.run_in_executor(
            None, functools.partial(
                collection.add,
                documents=[section_text],
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[{
                    "section_no": section_no,
                    "act": act
                }]
            )
        )
        print(f"✅ Stored: {section_no} | Act: {act} | ID: {doc_id[:8]}...")

async def main():
    print("🚀 Starting embedding process...")
    tasks = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            tasks.append(embed_and_store(os.path.join(DATA_DIR, filename)))
    await asyncio.gather(*tasks)
    print("✅ All files processed and embedded into ChromaDB.")

if __name__ == "__main__":
    asyncio.run(main())
