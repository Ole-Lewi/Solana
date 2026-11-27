import logging
from typing import Any

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from solana_ai.config import ProviderConfig

log = logging.getLogger(__name__)

#Errors that mean "this provider is unavailable right now, try the next one."
SWITCH_PROVIDER = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)

def _to_message(msg: Any) -> dict:
    out: dict[str, Any] = {"role": "assistant", "content": msg.content or ""}
    if msg.tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments":  tc.function.arguments or "{}",
                },
            }
            for tc in msg.tool_calls
        ]
    return out

class LLMClient:
    def __init__(self, providers: list[ProviderConfig]):
        self._clients = [
            (p, OpenAI(base_url=p.base_url, api_key=p.api_key, timeout=60, max_retries=0))
            for p in providers
        ]

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        last_error = None
        for provider, _client in self._clients:
            kwargs: dict[str, Any] = {"model": provider.model, "messages": messages}
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            try:
                response = _client.chat.completions.create(**kwargs)
                return _to_message(response.choices[0].message)
            except SWITCH_PROVIDER as err:
                last_error = err
                log.warning("Provider %s failed (%s); trying next.", provider.name, type(err).__name__)
        raise RuntimeError("All LLM providers failed.") from last_error