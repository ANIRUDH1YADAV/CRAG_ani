from indexing.vector_store import retrieve_chunks
from core.config import TOP_K_DOCUMENTS

def get_relevant_chunks(query: str):
    """Retrieve top‑k chunks from local vector store."""
    return retrieve_chunks(query, top_k=TOP_K_DOCUMENTS)