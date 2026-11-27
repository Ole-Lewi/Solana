import json
from solana_ai.registry import registry, Risk

@registry.register(risk=Risk.AUTO)
def add(a: int, b: int = 0) -> str:
    """Add two numbers and return their sum"""
    return str(a + b)

print(json.dumps(registry.schemas(), indent=2))
print(registry.get("add").fn(2, 3))