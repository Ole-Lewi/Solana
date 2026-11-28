import pytest

from solana_ai.tools.web import check_url

@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000",
        "http://localhost",
        "http://localhost:11434", #Ollama Server
        "http://169.254.169.254/latest/meta-data", #cloud metadata address
        "http://192.168.1.1", #typical home router
        "http://[::1]/",
        "file://C:/Windows/win.ini",
        "ftp://example.com",
    ],
)
def test_unsafe_urls_are_blocked(url):
    #Any message at all counts as "blocked". None would mean "safe to fetch".
    #These cases need no internet because they resolve locally.
    assert check_url(url) is not None