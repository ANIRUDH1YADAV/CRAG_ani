from tavily import TavilyClient
from core.config import TAVILY_API_KEY, TOP_K_WEB_RESULTS

_client = None

def get_tavily_client():
    global _client
    if _client is None:
        _client = TavilyClient(api_key=TAVILY_API_KEY)
    return _client

def web_search(query: str):
    """Fetch web results and return as list of documents."""
    # Guard against empty/None queries reaching Tavily (causes 400 Bad Request)
    if not query or not query.strip():
        print(f"web_search received an empty query, skipping search. Original: {query!r}")
        return []

    client = get_tavily_client()

    try:
        response = client.search(
            query.strip(),
            search_depth="basic",
            max_results=TOP_K_WEB_RESULTS or 3  # guard against 0/None
        )
    except Exception as e:
        print(f"Tavily search failed for query={query!r}: {e}")
        return []

    documents = []
    for i, result in enumerate(response.get("results", [])):
        documents.append({
            "id": f"web_{i}",
            "text": result["content"],
            "source": result["url"],
            "title": result["title"]
        })
    return documents