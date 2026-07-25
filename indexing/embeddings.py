from sentence_transformers import SentenceTransformer
import numpy as np
from core.config import EMBEDDING_MODEL

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_text(text: str) -> np.ndarray:
    model = get_embedding_model()
    return model.encode(text).tolist()

def embed_batch(texts: list) -> list:
    model = get_embedding_model()
    return model.encode(texts).tolist()