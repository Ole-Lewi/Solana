from solana_ai.tools.search import _clamp, _format

def test_clamp_keeps_result_count_sane():
    #The model picks max_results, so it must never be allowed to ask for 500
    assert _clamp(0) == 1
    assert _clamp(5) == 5
    assert _clamp(500) == 8

def test_format_handles_empty_and_missing_fields():
    assert _format([]) == "No results found."
    text = _format([{"title": "A headline", "url": "https://x.test", "source": "Src", "date": "2026-11-28"}])
    assert "A headline" in text and "https://x.test" in text
    assert "(Src | 2026-11-28)" in text
    #Scraped data often lacks fields. This must not crash.
    assert "(no title)" in _format([{}])