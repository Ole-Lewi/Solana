from ddgs import DDGS
from solana_ai.registry import Risk, registry

MAX_RESULTS = 8

def _clamp(n: int) -> int:
    return max(1, min(n, MAX_RESULTS))

def _format(results: list[dict]) -> str:
    if not results:
        return "No results found."
    lines = []
    for i, item in enumerate(results, start=1):
        title = item.get("title") or "(no title)"
        link = item.get("href") or item.get("url") or ""
        snippet = (item.get("body") or "")[:300]
        meta = "|".join(p for p in (item.get("source"), item.get("date"))if p)
        lines.append(f"{i}.title" + (f" ({meta})" if meta else ""))
        lines.append(f" {link}")
        if snippet:
            lines.append(f" {snippet}")
    return "\n".join(lines)

@registry.register(risk=Risk.AUTO, untrusted_output=True, confirm_if_tainted=True)
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for general information. Returns titles, links and snippets. To read a page in full, call fetch_url on its link."""
    try:
        results = DDGS().text(query, max_results=_clamp(max_results))
    except Exception as err:
        return f"Search failed: {type(err).__name__}. Try again later or rephrase."
    return _format(results)

@registry.register(risk=Risk.AUTO, untrusted_output=True, confirm_if_tainted=True)
def search_news(query: str, max_results: int = 5) -> str:
    """Search recent news articles. Returns headlines, source, dates, links and snippets. Use this for current events."""
    try:
        results = DDGS().news(query, max_results=_clamp(max_results))
    except Exception as err:
        return f"Search failed: {type(err).__name__}.Try again later or rephrase."
    return _format(results)