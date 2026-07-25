from core.groq_client import get_groq_client
from core.config import EVALUATOR_MODEL
from utils.prompts import SCORE_DOC_PROMPT

def score_document_relevance(query: str, document_text: str) -> float:
    """Whole‑document relevance score (0‑10)."""
    client = get_groq_client()
    prompt = SCORE_DOC_PROMPT.format(query=query, document=document_text)
    
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