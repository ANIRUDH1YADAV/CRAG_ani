# ----------------------------
#  Relevance Scoring (Sentence Level)
# ----------------------------
FILTER_PROMPT = """You are an expert relevance judge. Given a user query and a sentence, you must rate how relevant the sentence is to answering the query on a scale from 0 to 10.

**Score definitions:**
- **0** – Completely irrelevant, unrelated topic.
- **1‑2** – Barely relevant, perhaps a single word overlap but no useful information.
- **3‑4** – Somewhat relevant, mentions the topic but does not help answer the query.
- **5‑6** – Moderately relevant, contains partial information that could be useful.
- **7‑8** – Highly relevant, directly addresses the query with substantial information.
- **9‑10** – Perfectly relevant, provides a complete and accurate answer to the query.

Output **only the numeric score** (0‑10). Do not include any explanation, commentary, or extra text.

Query: {query}
Sentence: {strip}
Relevance score:"""

# ----------------------------
#  Relevance Scoring (Document / Chunk Level)
# ----------------------------
SCORE_DOC_PROMPT = """You are an expert relevance judge. Given a user query and a document (or a chunk of text), rate how well the document answers the query on a scale from 0 to 10.

**Score definitions:**
- **0** – Completely irrelevant.
- **1‑3** – Mostly irrelevant, maybe a few tangentially related words.
- **4‑6** – Partially relevant, contains some useful information but may be incomplete or off‑topic.
- **7‑8** – Highly relevant, directly addresses the query with substantial details.
- **9‑10** – Perfectly relevant, provides a comprehensive and accurate answer.

Output **only the numeric score** (0‑10). Do not add any commentary.

Query: {query}
Document:
{document}
Relevance score:"""

# ----------------------------
#  Query Rewriting for Web Search
# ----------------------------
REWRITE_PROMPT = """You are an expert at reformulating queries for web search. Rewrite the user's query to make it more effective for retrieving relevant results from a search engine. Follow these guidelines:
- Expand acronyms and abbreviations.
- Add relevant keywords that might be missing.
- Remove unnecessary words (e.g., "what is", "who is").
- Make the query specific and concise.
- Output **only the rewritten query** – no explanations, no extra text.

**Examples:**
Original: "what is ml"
Rewritten: machine learning definition applications

Original: "covid symptoms"
Rewritten: COVID-19 symptoms signs treatment

Original: "who wrote death of a batman"
Rewritten: Death of a Batman screenwriter author

Now rewrite this query:
Original query: {query}
Rewritten query:"""

# ----------------------------
#  Final Answer Generation (with citations)
# ----------------------------
GENERATE_PROMPT = """You are a helpful assistant that answers questions based strictly on the provided context. Follow these rules:

1. Before answering, you may reason step‑by‑step inside <think>...</think> tags. Then provide your final answer outside those tags.
2. **Answer using only the context.** Do not use any external knowledge.
3. If the context does **not** contain enough information to answer the question, say: "I don't have enough information to answer this."
4. At the end of your answer, **cite the exact sentences from the context** that support your answer. Use quotation marks and, if available, mention the source document name.

Context:
{context}

Question: {query}

Answer:"""