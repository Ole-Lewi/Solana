import re
from pathlib import Path
from datetime import datetime

from solana_ai.agent import SolanaAgent
from solana_ai.llm import LLMClient
from solana_ai.registry import registry, Risk
from solana_ai.config import load_providers
from solana_ai.permissions import PermissionGate

@registry.register(risk=Risk.AUTO)
def add(a: int, b: int = 0) -> str:
    """Add two numbers and return their sum."""
    return str(a + b)

@registry.register(risk=Risk.AUTO)
def get_time() -> str:
    """return the current local time and date on the user's laptop."""
    return datetime.now().isoformat(timespec="seconds")

@registry.register(risk=Risk.CONFIRM)
def save_note(title: str, content: str) -> str:
    """Save a short text note as a file in the user's SolanaNotes folder."""
    folder = Path.home() / "SolanaNotes"
    folder.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "note"
    target = folder / f"{slug}.txt"
    target.write_text(content, encoding="utf-8")
    return f"Saved note to {target}"


def ask_yes_no(prompt: str) -> bool:
    print(f"\n[approval needed] {prompt}")
    return input("    Allow? [y/N] ").strip().lower() in {"y", "yes"}


gate = PermissionGate(confirm=ask_yes_no)

agent = SolanaAgent(LLMClient(load_providers()), tools=registry, gate=gate)
history: list[dict] = []

while True:
    text = input("\nyou>").strip()
    if text == "/quit":
        break
    if not text:
        continue
    reply, history = agent.run_turn(history, text)
    print(f"solana> {reply}")