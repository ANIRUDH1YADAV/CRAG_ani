from pinecone import Pinecone
from core.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from indexing.embeddings import embed_text, embed_batch
from indexing.chunker import chunk_text

_pc = None
_index = None
BATCH_SIZE = 500
NAMESPACE = "documents"  # Pinecone equivalent of a Chroma "collection"


def get_chroma_collection():
    """Get or initialize the Pinecone index connection.
    (Name kept the same as before so no other file needs to change.)"""
    global _pc, _index
    if _pc is None:
        _pc = Pinecone(api_key=PINECONE_API_KEY)
    if _index is None:
        _index = _pc.Index(PINECONE_INDEX_NAME)
    return _index


def reset_collection():
    """Delete all existing vectors in the namespace so only the newly
    uploaded document is searchable. Call this BEFORE add_document()
    whenever a new file is uploaded."""
    index = get_chroma_collection()
    try:
        index.delete(delete_all=True, namespace=NAMESPACE)
        print("Namespace cleared. Ready for new document.")
    except Exception as e:
        # namespace may not exist yet on first run — safe to ignore
        print(f"No existing vectors to delete (fine on first run): {e}")


def add_document(doc_id: str, text: str, metadata: dict = None):
    """Split document into chunks and upsert to Pinecone."""
    chunks = chunk_text(text)
    if not chunks:
        print(f"No chunks generated for {doc_id}")
        return

    try:
        embeddings = embed_batch(chunks)
    except Exception as e:
        print(f"Embedding failed: {e}")
        return

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

    # Pinecone stores metadata as key/value pairs alongside each vector.
    # We keep the chunk text inside metadata, same as Chroma did.
    metadatas = [
        {
            "doc_id": doc_id,
            "source": metadata.get("source", "") if metadata else "",
            "chunk_index": i,
            "text": chunk
        }
        for i, chunk in enumerate(chunks)
    ]

    index = get_chroma_collection()

    # Pinecone expects a list of (id, vector, metadata) tuples per batch
    for i in range(0, len(chunks), BATCH_SIZE):
        batch_ids = ids[i:i + BATCH_SIZE]
        batch_embeddings = embeddings[i:i + BATCH_SIZE]
        batch_metadatas = metadatas[i:i + BATCH_SIZE]

        vectors = list(zip(batch_ids, batch_embeddings, batch_metadatas))
        index.upsert(vectors=vectors, namespace=NAMESPACE)

    print(f"Added {len(chunks)} chunks from '{doc_id}'.")


def retrieve_chunks(query: str, top_k: int = 5):
    """Retrieve top-k chunks from Pinecone."""
    query_emb = embed_text(query)
    index = get_chroma_collection()

    results = index.query(
        vector=query_emb,
        top_k=top_k,
        namespace=NAMESPACE,
        include_metadata=True
    )

    chunks = []
    for match in results["matches"]:
        meta = match["metadata"]
        chunks.append({
            "id": match["id"],
            "text": meta.get("text", ""),
            "source": meta.get("source", "unknown"),
            "doc_id": meta.get("doc_id", ""),
            "chunk_index": meta.get("chunk_index", 0),
            "relevance": match["score"]  # cosine score: already similarity, higher = better
        })
    return chunks