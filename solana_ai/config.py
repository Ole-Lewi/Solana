import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str
    model: str
    api_key: str = field(repr=False)

def _read_provider(prefix: str, name: str) -> ProviderConfig | None:
    base_url = os.getenv(f"{prefix}_BASE_URL")
    model = os.getenv(f"{prefix}_MODEL")
    if not base_url or not model:
        return None
    api_key = os.getenv(f"{prefix}_API_KEY") or "none"
    return ProviderConfig(name, base_url, model, api_key)

def load_providers() -> list[ProviderConfig]:
    found = [
        _read_provider("PRIMARY", "primary"),
        _read_provider("FALLBACK", "fallback"),
    ]
    providers = [p for p in found if p is not None]
    if not providers:
        raise RuntimeError("No LLM provider configures. Check your .env file.")
    return providers