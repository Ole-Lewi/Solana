import re
import ipaddress
import socket
from urllib.parse import urljoin, urlparse
import httpx

from solana_ai.registry import Risk, registry

try:
    import trafilatura
except ImportError:
    trafilatura=None

MAX_REDIRECTS = 3
MAX_BYTES = 1_000_000

def check_url(url: str) -> str|None:
    """Return an error message if the URL is unsafe to fetch, else None."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "Only http(s) URLs are allowed."
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        return f"Could not resolve host: {parsed.hostname}"
    for info in infos:
        ip = ipaddress.ip_address(str(info[4][0]).split("%")[0])
        if not ip.is_global:
            return "Blocked: that address is not in the public internet."
        return None

def _extract_text(html: str) -> str:
    if trafilatura is not None:
        extracted = trafilatura.extract(html)
        if extracted:
            return extracted
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html)
    text = re.sub(r"(?s<[^>]+>)", "", text)
    return re.sub(r"\s+", "", text).strip()

@registry.register(risk=Risk.AUTO, untrusted_output=True, confirm_if_tainted=True)
def fetch_url(url: str, max_chars: int = 4000) -> str:
    current = url
    headers = {"User-Agent": "Solana/0.1"}
    with httpx.Client(timeout=15, follow_redirects=False, headers=headers) as client:
        for _ in range(MAX_REDIRECTS + 1):
            if error :=check_url(current):
                return error
            try:
                with client.stream("GET", current) as response:
                    if response.is_redirect and "location" in response.headers:
                        current = urljoin(current, response.headers["location"])
                        continue
                    if response.status_code >= 400:
                        return f"HTTP{response.status_code} from {current}"
                    content_type = response.headers.get("content-type", "")
                    if "html" not in content_type and "text" not in content_type:
                        return f"Unsupported content type: {content_type or 'unknown'}"
                    body=b""
                    for chunk in response.iter_bytes():
                        body +=chunk
                        if len(body) > MAX_BYTES:
                            break
                    html = body.decode(response.encoding or "utf-8", errors="replace")
            except httpx.HTTPError as err:
                return f"Request failed: {type(err).__name__}"
            return _extract_text(html)[:max_chars]
        return "Too many redirects."