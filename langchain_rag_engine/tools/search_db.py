# backend/tools/search_db.py

from chromadb import PersistentClient

client = PersistentClient(path="./chroma_db")
collection = client.get_collection("legal_assistant")

def search_vector_db(query: str) -> list[str]:
    print(f"[Tool: search_db] Searching vector DB for: {query}")
    result = collection.query(query_texts=[query], n_results=3)
    return result["documents"][0] if result["documents"] else []

def keyword_section_search(query: str) -> list[str]:
    import re
    match = re.search(r"Section\s+(\d+)", query, re.IGNORECASE)
    if not match:
        return []

    section_number = match.group(1)
    section_key = f"Section {section_number}."

    print(f"[Tool: search_db] Performing keyword search for: {section_key}")
    result = collection.get(where={"section_no": {"$eq": section_key}})
    return result["documents"] if result["documents"] else []
