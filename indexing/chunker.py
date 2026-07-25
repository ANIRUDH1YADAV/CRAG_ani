def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split text into overlapping chunks of approximately `chunk_size` characters.
    Tries to break at sentence boundaries.
    """
    if not text:
        return []
    
    import nltk
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sent in sentences:
        # If adding this sentence exceeds chunk_size, start a new chunk
        if len(current_chunk) + len(sent) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Overlap: keep last `overlap` characters from current chunk
            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk = overlap_text + " " + sent
        else:
            if current_chunk:
                current_chunk += " " + sent
            else:
                current_chunk = sent
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks