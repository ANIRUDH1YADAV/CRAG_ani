# Corrective-RAG (CRAG) Chatbot for Document Question Answering

A production-ready **Corrective Retrieval-Augmented Generation (CRAG)** chatbot that enables users to upload documents (PDF, DOCX, and TXT), ask natural language questions, and receive context-aware responses using Large Language Models.

The system combines **semantic retrieval**, **retrieval evaluation**, **corrective filtering**, **query rewriting**, **web search fallback**, and **LLM-based answer generation** to improve response quality when retrieved documents are insufficient.

---

# Features

- Upload PDF, DOCX, and TXT documents
- Semantic document chunking
- Embedding generation using **all-MiniLM-L6-v2**
- Vector storage with **Pinecone**
- Semantic similarity search
- Retrieval evaluation using **Llama 3.1 8B**
- Corrective Retrieval (CRAG) pipeline
- Query rewriting for ambiguous queries
- Web search fallback using **Tavily**
- Context-aware answer generation using **Qwen3-32B**
- FastAPI backend
- React frontend
- Deployed using Render and Vercel

---

# Architecture

![Architecture](assets/architecture.png)

---

# Tech Stack

### Backend

- FastAPI
- LangChain
- Pinecone
- Sentence Transformers
- HuggingFace Embeddings
- Tavily Search API
- Groq API
- Python

### Frontend

- React
- Vite
- Axios

### Vector Database

- Pinecone

### Deployment

- Render
- Vercel

---

# Project Structure

```text
Corrective-RAG
│
├── api.py
├── app.py
├── requirements.txt
│
├── core/
├── evaluation/
├── generation/
├── indexing/
├── pipeline/
├── processing/
├── retrieval/
├── utils/
│
├── react-ui/
│
└── README.md
```

---

# Workflow

### 1. Document Upload

Users upload PDF, DOCX, or TXT documents.

↓

### 2. Document Processing

- Text extraction
- Cleaning
- Chunking

↓

### 3. Embedding Generation

Document chunks are converted into vector embeddings using **all-MiniLM-L6-v2**.

↓

### 4. Vector Storage

Embeddings are stored in **Pinecone**.

↓

### 5. Query Processing

The user submits a natural language query.

↓

### 6. Retrieval

Top-K relevant chunks are retrieved from the vector database.

↓

### 7. Retrieval Evaluation

Each retrieved document is scored by an LLM and classified as:

- Correct
- Ambiguous
- Incorrect

↓

### 8. Corrective Retrieval

Depending on the evaluation:

- Retrieve documents directly
- Rewrite the query
- Perform web search using Tavily

↓

### 9. Context Construction

Relevant document chunks and web search results are combined into a unified context.

↓

### 10. Answer Generation

The final answer is generated using **Qwen3-32B**.

---

# API Endpoints

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/upload` | Upload documents |
| POST | `/query` | Ask questions |
| GET | `/health` | Health check |

---

# Deployment

### Backend

**Render**

### Frontend

**Vercel**

---

# Future Enhancements

- Hybrid Search (Dense + Sparse Retrieval)
- Cross-Encoder Reranking
- Streaming Responses
- Multi-document Conversations
- Authentication
- Citation Highlighting
- Conversation Memory

---

# Acknowledgements

This project is based on the **Corrective Retrieval-Augmented Generation (CRAG)** methodology and provides a practical implementation using FastAPI, React, Pinecone, Tavily Search, and modern Large Language Models.

---

# Author

**Anirudh Yadav**

GitHub: https://github.com/ANIRUDH1YADAV
