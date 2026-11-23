import json
from solana_ai.llm import LLMClient
from solana_ai.registry import ToolRegistry

SYSTEM_PROMPT = (
    "You are Solana, a concise AI personal assistant running on the user's laptop."
    "Use tools when they help. Never invent tool results."
    "If a tool fails, say so honestly."
)

class SolanaAgent:
    def __init__(self, llm: LLMClient, tools: ToolRegistry, max_rounds: int = 8):
        self.llm = llm
        self.tools = tools
        self.max_rounds = max_rounds

    def run_turn(self, history: list[dict], user_text: str) -> tuple[str, list[dict]]:
        messages = [*history, {"role": "user", "content": user_text}]

        for _ in range(self.max_rounds):
            full = [{"role": "user", "content": SYSTEM_PROMPT}, *messages]
            reply = self.llm.chat(full, self.tools.schemas())
            messages.append(reply)