import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Thresholds
UPPER_THRESHOLD = float(os.getenv("UPPER_THRESHOLD", 8.0))
LOWER_THRESHOLD = float(os.getenv("LOWER_THRESHOLD", 3.0))
STRIP_THRESHOLD = float(os.getenv("STRIP_THRESHOLD", 5.0))

# Retrieval
TOP_K_DOCUMENTS = int(os.getenv("TOP_K_DOCUMENTS", 5))
TOP_K_WEB_RESULTS = int(os.getenv("TOP_K_WEB_RESULTS", 3))

# Models
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "qwen/qwen3-32b")
EVALUATOR_MODEL = os.getenv("EVALUATOR_MODEL", "llama-3.1-8b-instant")

# Embedding
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PERSIST_DIR = "chroma_data"


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")