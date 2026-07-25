from core.config import UPPER_THRESHOLD, LOWER_THRESHOLD

def classify_documents(doc_scores: list) -> str:
    """
    doc_scores: list of (document, score)
    Returns 'correct', 'ambiguous', or 'incorrect'.
    """
    if not doc_scores:
        return "incorrect"
    
    max_score = max(score for _, score in doc_scores)
    
    if max_score >= UPPER_THRESHOLD:
        return "correct"
    elif any(LOWER_THRESHOLD < score < UPPER_THRESHOLD for _, score in doc_scores):
        return "ambiguous"
    else:
        return "incorrect"