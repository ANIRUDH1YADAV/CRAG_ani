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
    client = get_tavily_client()
    response = client.search(query, search_depth="basic", max_results=TOP_K_WEB_RESULTS)
    
    documents = []
    for i, result in enumerate(response["results"]):
        documents.append({
            "id": f"web_{i}",
            "text": result["content"],
            "source": result["url"],
            "title": result["title"]
        })
    return documents