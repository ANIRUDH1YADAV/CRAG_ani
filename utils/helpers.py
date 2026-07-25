def format_sources(sources: list) -> str:
    """Convert source list into readable string for frontend."""
    formatted = []
    for src in sources:
        if src.get("url"):
            formatted.append(f"- {src['title']} ({src['url']})")
        else:
            formatted.append(f"- {src['source']}")
        # Optionally add used strips
        for s in src.get("strips_used", [])[:2]:  # show only first 2
            formatted.append(f"  → {s[:100]}...")
    return "\n".join(formatted)