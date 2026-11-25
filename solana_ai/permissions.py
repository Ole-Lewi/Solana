import json
from dataclasses import dataclass
from typing import Any, Callable

from solana_ai.registry import Risk, Tool

def wrap_untrusted(text: str, source: str) -> str:
    safe = text.replace("</untrusted_content>", "[/untrusted_content]")
    return f'<untrusted_content source="{source}">\{safe}\n</untrusted_content>'

@dataclass
class PermissionGate:
    confirm: Callable[[str], bool]
    tainted: bool =False

    def reset_turn(self) -> None:
        self.tainted = False

    def record_result(self, tool: Tool) -> None:
        if tool.untrusted_output:
            self.tainted = True

    def authorize(self, tool: Tool, args: dict[str, Any]) -> tuple[bool, str]:
        if tool.risk is Risk.AUTO:
            return True, ""
        shown = json.dumps(args, ensure_ascii=False)
        if len(shown) > 600:
            shown = shown[:600] + "...(truncated)"
        if self.confirm(f"Solana wants to run {tool.name} with {shown}"):
            return True, ""
        return False, "the user denied this action. Do not retry it; tell the user it was not done."