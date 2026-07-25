import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}/pipeline/feature-extraction"

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


def _call_hf_api(texts: list[str]) -> list[list[float]]:
    """Call Hugging Face Inference API and return embeddings for a list of texts."""
    response = requests.post(
        HF_API_URL,
        headers=HEADERS,
        json={"inputs": texts, "options": {"wait_for_model": True}},
        timeout=60
    )
    response.raise_for_status()
    result = response.json()

    # HF sometimes returns [batch, tokens, dims] for feature-extraction —
    # mean-pool over tokens if that shape is returned instead of [batch, dims]
    embeddings = []
    for item in result:
        if isinstance(item[0], list):
            # token-level embeddings: mean pool to a single sentence vector
            num_tokens = len(item)
            dims = len(item[0])
            pooled = [
                sum(item[t][d] for t in range(num_tokens)) / num_tokens
                for d in range(dims)
            ]
            embeddings.append(pooled)
        else:
            embeddings.append(item)
    return embeddings


def embed_text(text: str) -> list[float]:
    """Embed a single string, returns a single 384-dim vector."""
    return _call_hf_api([text])[0]


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings, returns a list of 384-dim vectors."""
    if not texts:
        return []

    # HF free tier works best with small batches — chunk requests
    BATCH_SIZE = 32
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        all_embeddings.extend(_call_hf_api(batch))
    return all_embeddings