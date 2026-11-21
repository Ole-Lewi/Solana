import json
from solana_ai.config import load_providers
from solana_ai.llm import LLMClient
from solana_ai.registry import registry, Risk

@registry.register(risk=Risk.AUTO)
def add(a: int, b: int = 0) -> str:
    "Add two numbers and return their sum."
    return str(a + b)

from datetime import datetime
@registry.register(risk=Risk.AUTO)
def get_time() -> str:
    """Return the current local date and time on the user's laptop."""
    return datetime.now().isoformat(timespec="seconds")


client = LLMClient(load_providers())
messages = [
    {
        "role": "system", "content": "You are Solana, a concise personal assistant. Use tools when helpful."
    },
    {
        "role": "user", "content": "What is the capital city of Kenya?"
    },
]
reply = client.chat(messages, registry.schemas())
print(reply)

messages.append(reply)
for call in reply.get("tool_calls", []):
    args = json.loads(call["function"]["arguments"])
    tool = registry.get(call["function"]["name"])
    assert tool is not None
    result = tool.fn(**args)
    messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})

print(client.chat(messages, registry.schemas())["content"])