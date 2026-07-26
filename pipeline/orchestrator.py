from retrieval.retriever import get_relevant_chunks   # <-- changed
from retrieval.web_search import web_search
from evaluation.document_scorer import score_document_relevance
from evaluation.decision import classify_documents
from processing.stripper import split_sentences
from processing.filter import filter_strips
from processing.merger import merge_kept_strips
from generation.generator import generate_answer
from utils.prompts import REWRITE_PROMPT
from core.groq_client import get_groq_client
from core.config import LOWER_THRESHOLD, UPPER_THRESHOLD, EVALUATOR_MODEL

def rewrite_query(query: str) -> str:
    client = get_groq_client()
    prompt = REWRITE_PROMPT.format(query=query)
    response = client.chat.completions.create(
        model=EVALUATOR_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=100,
        extra_body={"reasoning_effort": "none"}  # SDK 0.9.0 doesn't support this as a direct kwarg
    )
    return response.choices[0].message.content.strip()

def refine_document(doc: dict, query: str, doc_score: float = None):
    """Split, filter, merge a single chunk."""
    strips = split_sentences(doc["text"])
    kept = filter_strips(query, strips)
    if not kept:
        # If chunk is highly relevant but no strips passed, keep entire chunk
        if doc_score and doc_score >= UPPER_THRESHOLD:
            return {
                "text": doc["text"],
                "source": doc.get("source", doc.get("url", "unknown")),
                "strips_used": [doc["text"][:200] + "..."]
            }
        return None
    return merge_kept_strips(kept, doc.get("source", doc.get("url", "unknown")))

def answer_query(query: str):
    """Main pipeline: retrieve chunks → evaluate → classify → refine → generate."""
    trace = {
        "query": query,
        "retrieved_chunks": [],      # renamed for clarity
        "chunk_scores": [],           # renamed
        "classification": None,
        "refined_local": [],
        "web_search_used": False,
        "web_results": [],
        "final_context": "",
        "sources": []
    }

    # 1. Retrieve top‑k chunks
    chunks = get_relevant_chunks(query)
    trace["retrieved_chunks"] = [
        {"id": c["id"], "source": c["source"], "text_preview": c["text"][:200]}
        for c in chunks
    ]

    # 2. Score each chunk with LLM
    chunk_scores = []
    for chunk in chunks:
        score = score_document_relevance(query, chunk["text"])
        chunk_scores.append((chunk, score))
        trace["chunk_scores"].append({
            "chunk_id": chunk["id"],
            "source": chunk["source"],
            "score": score
        })

    # 3. Classify based on chunk scores
    classification = classify_documents(chunk_scores)
    trace["classification"] = classification

    context_pieces = []
    sources = []

    # 4. Conditional refinement & web fallback
    if classification == "correct":
        best_chunks = [chunk for chunk, score in chunk_scores if score >= UPPER_THRESHOLD]
        for chunk in best_chunks[:1]:  # take top 1
            refined = refine_document(chunk, query, score)
            if refined:
                context_pieces.append(refined["text"])
                sources.append({
                    "source": chunk["source"],
                    "strips_used": refined["strips_used"]
                })
                trace["refined_local"].append({
                    "chunk_id": chunk["id"],
                    "strips_kept": len(refined["strips_used"]),
                    "preview": refined["text"][:200]
                })

    elif classification == "ambiguous":
        useful_local = [chunk for chunk, score in chunk_scores if score > LOWER_THRESHOLD]
        for chunk in useful_local:
            refined = refine_document(chunk, query, score)
            if refined:
                context_pieces.append(refined["text"])
                sources.append({
                    "source": chunk["source"],
                    "strips_used": refined["strips_used"]
                })
                trace["refined_local"].append({
                    "chunk_id": chunk["id"],
                    "strips_kept": len(refined["strips_used"]),
                    "preview": refined["text"][:200]
                })

        # Web search
        trace["web_search_used"] = True
        rewritten = rewrite_query(query)
        trace["rewritten_query"] = rewritten
        web_docs = web_search(rewritten)
        trace["web_results"] = [
            {"title": w.get("title"), "url": w["source"], "preview": w["text"][:200]}
            for w in web_docs
        ]
        for wdoc in web_docs:
            refined = refine_document(wdoc, query)
            if refined:
                context_pieces.append(refined["text"])
                sources.append({
                    "source": wdoc["source"],
                    "title": wdoc.get("title", ""),
                    "url": wdoc["source"],
                    "strips_used": refined["strips_used"]
                })

    else:  # incorrect
        trace["web_search_used"] = True
        rewritten = rewrite_query(query)
        trace["rewritten_query"] = rewritten
        web_docs = web_search(rewritten)
        trace["web_results"] = [
            {"title": w.get("title"), "url": w["source"], "preview": w["text"][:200]}
            for w in web_docs
        ]
        for wdoc in web_docs:
            refined = refine_document(wdoc, query)
            if refined:
                context_pieces.append(refined["text"])
                sources.append({
                    "source": wdoc["source"],
                    "title": wdoc.get("title", ""),
                    "url": wdoc["source"],
                    "strips_used": refined["strips_used"]
                })

    # 5. Final context
    final_context = "\n\n---\n\n".join(context_pieces) if context_pieces else "No relevant information found."
    trace["final_context"] = final_context[:500]
    trace["sources"] = sources

    return generate_answer(query, final_context), sources, trace