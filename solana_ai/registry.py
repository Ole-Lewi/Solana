import inspect
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, get_type_hints

class Risk(str, Enum):
    AUTO = "auto"       #runs without asking
    CONFIRM = "confirm" #needs my explicit yes, every time

JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean"}

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Any]
    risk: Risk

    def validate(self, args: dict) -> str | None:
        try:
            inspect.signature(self.fn).bind(**args)
        except TypeError as err:
            return f"Invalid arguments for {self.name}: {err}"
        return None

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def validate(self, args: dict[str, Any]) -> str | None:
        try:
            inspect.signature(self.fn).bind(**args)
        except TypeError as err:
            return f"Invalid arguments for {self.name}: {err}"
        return None

def build_parameters(fn: Callable[..., Any]) -> dict[str, Any]:
    hints = get_type_hints(fn)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, param in inspect.signature(fn).parameters.items():
        properties[name] = {"type": JSON_TYPES.get(hints.get(name, str), "string")}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": properties, "required": required}

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, *, risk: Risk):
        def decorator(fn):
            self._tools[fn.__name__] = Tool(
                name=fn.__name__,
                description=" ".join((inspect.getdoc(fn) or "").split()),
                parameters=build_parameters(fn),
                fn=fn,
                risk=risk,
            )
            return fn
        return decorator

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]

registry = ToolRegistry()