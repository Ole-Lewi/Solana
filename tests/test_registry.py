from solana_ai.registry import Risk, registry

def test_schema_is_built_from_the_function_signature():
    params = registry.get("read_file").parameters
    assert params["required"] == ["path"]
    assert params["properties"]["max_chars"]["type"] == "integer"

def test_validate_rejects_junk_arguments():
    tool = registry.get("get_time")
    assert tool.validate({"": {}}) is not None
    assert tool.validate({}) is None

def test_unknown_tool_is_none():
    assert registry.get("delete_everything") is None

def test_save_note_must_stay_confirm():
    #Guard rail: if someone relaxes this label by accident, this test fails.
    assert registry.get("save_note").risk is Risk.CONFIRM

def test_tools_that_return_outside_content_are_flagged():
    for name in ("read_file", "list_dir", "fetch_url", "search_web", "search_news"):
        assert registry.get(name).untrusted_output, name
    for name in ("fetch_url", "search_web", "search_news"):
        assert registry.get(name).confirm_if_tainted, name