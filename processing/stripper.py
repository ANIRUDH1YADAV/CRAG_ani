import nltk

# Ensure punkt is downloaded
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def split_sentences(text: str) -> list:
    """Split text into sentence strips."""
    return nltk.sent_tokenize(text)