from solana_ai.llm import LLMClient
from solana_ai.registry import ToolRegistry
from solana_ai.permissions import PermissionGate

def __init__(self, llm: LLMClient, tools: ToolRegistry, gate: PermissionGate, max_rounds: int = 8):
    self.llm = llm
    self.tools = tools
    self.gate = gate
    self.max_rounds = max_rounds