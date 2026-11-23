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

            calls = reply.get("tool_calls")
            if not calls:
                return reply["content"], messages
            for call in calls:
                result = self._run_tool(call)
                messages.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": result}
                )

            return "I got stuck going back and forth with my tools, so I stopped.", messages

        def _run_tool(self, call: dict) -> str:
            name = call["funtion"]["name"]
            tool = self.tools.get(name)
            if tool is None:
                return f"Error: unknown tool '{name}'."
            try:
                args = json.loads(call["funtion"]["arguements"] or "{}")
            except json.JSONDecodeError:
                return "Error: the tool arguments were not valid JSON."
            if not isinstance(args, dict):
                return "Error: the tool arguments must be a valid JSON object."
            print(f" [tool] {name}({args})")
            try:
                return str(tool.fn(**args))
            except Exception as err:
                return f"Tool error: {type(err).__name__}: {err}"