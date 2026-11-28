import json

from solana_ai.agent import SolanaAgent, trim_history
from solana_ai.permissions import PermissionGate
from solana_ai.registry import registry

class FakeLLM:
    """Replays scripted model replies, so tests need to network, no API key and no luck."""
    def __init__(self, replies):
        self.replies = list(replies)

    def chat(self, messages, tools=None):
        #If the agent asks for more replies than we scripted, pop() raises: a useful signal.
        return self.replies.pop(0)

def call(name, args, call_id="c1", raw=None):
    #builds an assistance message that asks for one tool. "raw" lets us send broken JSON.
    arguments = raw if raw is not None else json.dumps(args)
    return {
        "role": "assistant",
        "content": "",
        "tool_calls": [{"id": call_id, "type":"function", "function": {"name": name, "arguments": arguments}}],

    }

def say(text):
    return{"role": "assistant", "content": text}

def make_agent(replies, confirm=lambda _: True, max_rounds=8):
    return SolanaAgent(
        llm=FakeLLM(replies),
        tools=registry,
        gate=PermissionGate(confirm=confirm),
        max_rounds=max_rounds,
    )

def tool_messages(history):
    return [m["content"] for m in history if m["role"] == "tool"]

def test_plain_answer_returns_text_and_history():
    reply, history = make_agent([say("hi")]).run_turn([], "hello")
    assert reply == "hi"
    assert history[0] == {"role": "user", "content": "hello"}

def test_denied_action_never_runs(tmp_path, monkeypatch):
    monkeypatch.setenv("SOLANA_NOTES_DIR", str(tmp_path))
    agent = make_agent([call("save_note", {"title": "x", "content": "y"}), say("not saved")], confirm=lambda _: False)
    reply, history = agent.run_turn([], "save a note")
    assert reply == "not saved"
    assert list(tmp_path.iterdir()) == [] #the real proof: nothing was written
    assert any("denied" in m for m in tool_messages(history))

def test_approved_action_runs(tmp_path, monkeypatch):
    monkeypatch.setenv("SOLANA_ALLOWED_ROOTS", str(tmp_path))
    agent = make_agent([call("save_note", {"title": "Plan", "content": "ship it"}), say("saved")])
    agent.run_turn([], "save a note")
    assert (tmp_path / "plan.txt").read_text(encoding="utf-8") == "ship it"