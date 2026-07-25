from core.groq_client import get_groq_client
from core.config import EVALUATOR_MODEL, STRIP_THRESHOLD
from utils.prompts import FILTER_PROMPT

def score_strip(query: str, strip: str) -> float:
    """Use LLM to rate relevance of a single strip (0‑10)."""
    client = get_groq_client()
    prompt = FILTER_PROMPT.format(query=query, strip=strip)
    
    response = client.chat.completions.create(
        model=EVALUATOR_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10
    )
    try:
        score = float(response.choices[0].message.content.strip())
        return max(0.0, min(10.0, score))
    except:
        return 0.0

def filter_strips(query: str, strips: list) -> list:
    """Keep only strips with score ≥ STRIP_THRESHOLD."""
    kept = []
    for strip in strips:
        score = score_strip(query, strip)
        if score >= STRIP_THRESHOLD:
            kept.append((strip, score))
    return kept