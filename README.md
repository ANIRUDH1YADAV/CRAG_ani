# CRAG — Corrective Retrieval-Augmented Generation

> A production-ready corrective RAG pipeline with **tunable relevance thresholds**, **multi-level refinement**, **web search fallback**, and **forced citations** — designed to drastically reduce hallucinations and keep every answer grounded in verified information.

---

## Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [How It Works](#-how-it-works)
  - [1. Document Ingestion](#1-document-ingestion)
  - [2. Query Processing & Retrieval](#2-query-processing--retrieval)
  - [3. Evaluation & Classification](#3-evaluation--classification)
  - [4. Refinement & Fallback](#4-refinement--fallback)
  - [5. Generation](#5-generation)
- [Configuration](#-configuration)
- [Hallucination Prevention](#-hallucination-prevention)
- [Tech Stack](#-tech-stack)
- [License](#-license)

---

## Overview

CRAG implements a sophisticated **Corrective RAG** pipeline that uses tunable relevance thresholds to decide whether local documents are sufficient, need refinement, or require a web search fallback.

By scoring both **entire chunks** and **individual sentences**, and by forcing the generator to **cite its sources**, the system drastically reduces hallucinations and ensures answers are grounded in verified information.

The pipeline operates in five main phases:

| Phase | Description |
|-------|-------------|
| **Document Ingestion** | Uploaded files (PDF, DOCX, TXT) are parsed, split into overlapping chunks, embedded, and stored in a vector database |
| **Query Processing** | A user question triggers retrieval of the most relevant chunks from the vector store |
| **Evaluation & Classification** | Each retrieved chunk is scored by an LLM `llama-3.1-8b-instant` (0–10). Based on configurable thresholds (UT, LT), results are classified as `Correct`, `Ambiguous`, or `Incorrect` |
| **Refinement & Fallback** | Chunks are refined at the sentence level; web search is triggered when local knowledge is insufficient |
| **Generation** | The final context is fed to `qwen/qwen3-32b`, which produces an answer with citations |

---
##  Architecture


![CRAG Pipeline Flowchart](CRAG.jpg)


---


## Features

- **Threshold-based evaluation** — tunable `UPPER_THRESHOLD` and `LOWER_THRESHOLD` to control strictness
- **Two-stage verification** — chunk-level scoring followed by sentence-level filtering
- **Web search fallback** — Tavily API triggered automatically when local documents are insufficient
- **Query rewriting** — LLM rewrites ambiguous/failed queries to be more search-engine-friendly
- **Forced citations** — generator must cite exact supporting sentences, combating hallucinations
- **Streaming output** — answers streamed token-by-token for real-time feedback
- **Full transparency** — Streamlit UI exposes pipeline trace, scores, sources, and model reasoning
- **Persistent vector store** — ChromaDB saves indexed chunks; re-indexing only needed on document changes


## Getting Started

### Prerequisites

- Python 3.9+
- A [Groq](https://console.groq.com) API key (for LLM inference)
- A [Tavily](https://tavily.com) API key (for web search fallback)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/CRAG.git
cd CRAG

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the example env file and fill in your keys
cp .env.example .env
```

### Environment Variables

Create a `.env` file in the root directory (see `.env.example`):

```dotenv
# Groq API
GROQ_API_KEY=your_groq_api_key_here

# Tavily API (for web search)
TAVILY_API_KEY=your_tavily_api_key_here

# Thresholds (tune these as needed)
UPPER_THRESHOLD=8.0      # UT – Correct if score ≥ UT
LOWER_THRESHOLD=3.0      # LT – Incorrect if score ≤ LT
STRIP_THRESHOLD=5.0      # Minimum relevance to keep a sentence strip

# Retrieval settings
TOP_K_DOCUMENTS=5        # Number of documents to retrieve from vector store
TOP_K_WEB_RESULTS=3      # Number of web results to fetch

# Model names
GENERATOR_MODEL=qwen/qwen3-32b
EVALUATOR_MODEL=llama-3.1-8b-instant
```

### Running the App

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## How It Works

### 1. Document Ingestion

Upload PDF, DOCX, or TXT files via the sidebar. The pipeline:
- Parses raw text using `pypdf`, `python-docx`, or built-in I/O
- Splits text into **~500-character overlapping chunks** (50-char overlap) using NLTK sentence boundaries to avoid mid-sentence breaks
- Embeds each chunk using `sentence-transformers/all-MiniLM-L6-v2`
- Stores chunks in a **persistent ChromaDB** collection with metadata

### 2. Query Processing & Retrieval

A user question is embedded and used to query ChromaDB. The top-`k` most similar chunks (default: 5) are retrieved using cosine similarity.

### 3. Evaluation & Classification

Each retrieved chunk is scored **0–10** by `llama-3.1-8b-instant` using a detailed relevance rubric. The maximum score across all chunks determines classification:

| Condition | Classification |
|-----------|---------------|
| `max_score ≥ UPPER_THRESHOLD` | **Correct** — local docs are sufficient |
| Any score between `LT` and `UT` | **Ambiguous** — local docs partially relevant |
| All scores `< LOWER_THRESHOLD` | **Incorrect** — local docs insufficient |

### 4. Refinement & Fallback

| Classification | Action |
|---------------|--------|
| **Correct** | Refine only the top-scoring chunk(s) |
| **Ambiguous** | Refine all moderately relevant chunks + trigger web search |
| **Incorrect** | Skip local docs entirely, use web search only |

**Refinement process** for each chunk:
1. Split into individual sentences (`stripper.py`)
2. Score each sentence against the query (`filter.py`, LLM-based)
3. Keep sentences with score ≥ `STRIP_THRESHOLD`
4. Merge kept sentences into a clean context block (`merger.py`)

> If a chunk is highly relevant but no single sentence passes the threshold, the full chunk is kept as a fallback to prevent information loss.

**Web search** uses Tavily with an LLM-rewritten query (optimised for search engines). Web results undergo the same refinement process as local chunks.

### 5. Generation

The final merged context (local + web) is passed to `qwen/qwen3-32b` with a prompt that:
- Restricts the model to answer **only from the provided context**
- **Forces citation** of exact supporting sentences
- Falls back to "I don't have enough information" if context is insufficient

The response is streamed live in the Streamlit UI.

---

## Configuration (Tunable)

| Variable | Default | Description |
|----------|---------|-------------|
| `UPPER_THRESHOLD` | `8.0` | Minimum score to classify a chunk as **Correct** |
| `LOWER_THRESHOLD` | `3.0` | Maximum score to classify a chunk as **Incorrect** |
| `STRIP_THRESHOLD` | `5.0` | Minimum sentence score to keep during refinement |
| `TOP_K_DOCUMENTS` | `5` | Number of chunks to retrieve from ChromaDB |
| `TOP_K_WEB_RESULTS` | `3` | Number of Tavily web results to fetch |
| `GENERATOR_MODEL` | `qwen/qwen3-32b` | Model for final answer generation |
| `EVALUATOR_MODEL` | `llama-3.1-8b-instant` | Model for scoring and query rewriting |

> **Tip:** Raise `UPPER_THRESHOLD` to make the system more conservative before accepting local documents. Lower `STRIP_THRESHOLD` to keep more sentences during refinement.

---

## Hallucination Prevention

CRAG employs five complementary strategies to minimise hallucinations:

1. **Two-stage verification** — Chunks are scored by an LLM; only those above thresholds are used. Then individual sentences are scored again. This double-checking filters out irrelevant content before it reaches the generator.

2. **Context restriction** — The generator receives *only* the merged, filtered context. It is explicitly instructed to answer based solely on that context — not its internal training knowledge.

3. **Forced citations** — By requiring the model to cite exact supporting sentences, every claim must be traceable to a source. If no supporting sentence exists, the model responds with "I don't have enough information."

4. **Web fallback** — When local knowledge is insufficient, real-world data is fetched instead of relying on the generator's potentially outdated or incorrect internal knowledge.

5. **Full transparency** — The Streamlit UI exposes the complete pipeline trace: all scores, classification decisions, refined chunks, web results, and context preview — so users can verify and debug every response.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **UI** | [Streamlit](https://streamlit.io) |
| **LLM Inference** | [Groq](https://groq.com) (`llama-3.1-8b-instant`, `qwen/qwen3-32b`) |
| **Embeddings** | [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| **Vector Store** | [ChromaDB](https://www.trychroma.com/) (persistent) |
| **Web Search** | [Tavily](https://tavily.com) |
| **PDF Parsing** | [pypdf](https://pypdf.readthedocs.io) |
| **DOCX Parsing** | [python-docx](https://python-docx.readthedocs.io) |
| **Tokenisation** | [NLTK](https://www.nltk.org/) (`sent_tokenize`) |

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file included in this repository.

---

## References

- Research Paper - [Corrective Retrieval Augmented Generation](https://arxiv.org/pdf/2401.15884)

<p align="center">
  Built with ❤️ using Streamlit
</p>