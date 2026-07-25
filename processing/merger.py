def merge_kept_strips(kept_strips: list, doc_source: str) -> dict:
    """
    kept_strips: list of (strip_text, score)
    Returns dict with merged text and source metadata.
    """
    merged_text = " ".join([s for s, _ in kept_strips])
    return {
        "text": merged_text,
        "source": doc_source,
        "strips_used": [s for s, _ in kept_strips],
        "scores": [score for _, score in kept_strips]
    }