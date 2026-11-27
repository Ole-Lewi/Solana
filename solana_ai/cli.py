import logging
import os

from solana_ai.agent import SolanaAgent
from solana_ai.config import load_providers
from solana_ai.llm import LLMClient
from solana_ai.permissions import PermissionGate
from solana_ai.tools import registry

def ask_yes_no(prompt: str) -> bool:
    print(f"\n[approval needed] {prompt}")
    return input(" Allow? [y/N]").strip().lower() in {"y", "yes"}

def main() -> None:
    level = logging.INFO if os.getenv("SOLANA_DEBUG") else logging.WARNING
    logging.basicConfig(level=level, format="[%(name)s] %(message)s")

    agent = SolanaAgent(
        llm=LLMClient(load_providers()),
        tools=registry,
        gate=PermissionGate(confirm=ask_yes_no),
    )
    history: list[dict] = []
    print("Solana is ready. /reset clears the conversation, /quit exits.")

    while True:
        try:
            text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/reset":
            history = []
            print("Conversation cleared.")
            continue
        try:
            reply, history = agent.run_turn(history, text)
        except RuntimeError as err:
            print (f"solana> I can't reach any model right now ({err}).")
            continue
        print(f"\nsolana> {reply}")