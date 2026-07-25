from core.groq_client import get_groq_client
from core.config import GENERATOR_MODEL
from utils.prompts import GENERATE_PROMPT

def generate_answer(query: str, context: str) -> str:
    """Produce final answer using the generator model."""
    client = get_groq_client()
    prompt = GENERATE_PROMPT.format(query=query, context=context)
    
    completion = client.chat.completions.create(
        model=GENERATOR_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=1024,
        stream=True
    )
    
    full_response = ""
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        full_response += content
        yield content  # for streaming
    return full_response  # not used directly when streaming