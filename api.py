import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline.orchestrator import answer_query
from indexing.document_loader import load_document
from indexing.vector_store import add_document, reset_collection

app = FastAPI(title="Corrective RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keeps track of currently indexed filenames (server-side, simple in-memory state)
_indexed_files = []


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list
    trace: dict


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    result, sources, trace = answer_query(request.question)

    # generate_answer() returns a stream/generator, not a plain string
    if isinstance(result, str):
        answer = result
    else:
        answer = "".join(chunk for chunk in result)

    return {"answer": answer, "sources": sources, "trace": trace}


@app.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    """Clears the existing collection, then indexes all uploaded files."""
    global _indexed_files
    reset_collection()
    _indexed_files = []

    for file in files:
        suffix = Path(file.filename).suffix
        contents = await file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        text = load_document(tmp_path)
        os.unlink(tmp_path)

        add_document(
            doc_id=file.filename,
            text=text,
            metadata={"source": file.filename}
        )
        _indexed_files.append(file.filename)

    return {"indexed_files": _indexed_files}


@app.get("/indexed-files")
def get_indexed_files():
    return {"indexed_files": _indexed_files}


@app.get("/thresholds")
def get_thresholds():
    return {
        "upper_threshold": float(os.getenv("UPPER_THRESHOLD", 8.0)),
        "lower_threshold": float(os.getenv("LOWER_THRESHOLD", 3.0)),
        "strip_threshold": float(os.getenv("STRIP_THRESHOLD", 5.0)),
    }


@app.get("/health")
def health():
    return {"status": "ok"}