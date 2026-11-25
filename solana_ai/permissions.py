import json
from dataclasses import dataclass
from typing import Any, Callable

from solana_ai.registry import Risk, Tool

@dataclass
class PermissionGate:
    confirm: Callable[[str], bool]

    def authorize(self, tool: Tool, args: dict[str, Any]) -> tuple[bool, str]:
        if tool.risk is Risk.AUTO:
            return True, ""
        shown = json.dumps(args, ensure_ascii=False)
        if len(shown) > 600:
            shown = shown[:600] + "...(truncated)"
        if self.confirm(f"Solana wants to run {tool.name} with {shown}"):
            return True, ""
        return False, "the user denied this action. Do not retry it; tell the user it was not done."