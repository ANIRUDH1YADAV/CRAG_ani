import re
from core.groq_client import get_groq_client
from core.config import EVALUATOR_MODEL
from utils.prompts import SCORE_DOC_PROMPT

def score_document_relevance(query: str, document_text: str) -> float:
    """Whole-document relevance score (0-10)."""
    client = get_groq_client()
    prompt = SCORE_DOC_PROMPT.format(query=query, document=document_text)

    response = client.chat.completions.create(
        model=EVALUATOR_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=50  # gpt-oss models can return extra tokens/reasoning, give it room
    )

    raw_content = response.choices[0].message.content.strip()

    try:
        # Try direct parse first (ideal case: model just returns "7")
        score = float(raw_content)
    except ValueError:
        # Fallback: extract the first number found anywhere in the response
        # (handles cases like "Score: 7" or "7/10" or reasoning text with a number)
        match = re.search(r"-?\d+(\.\d+)?", raw_content)
        if match:
            score = float(match.group())
        else:
            print(f"Could not parse a score from model output: {raw_content!r}")
            return 0.0

    return max(0.0, min(10.0, score))