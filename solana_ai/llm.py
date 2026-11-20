import logging

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

class LLMClient:
    def __init__(self, providers: list[ProviderConfig]):
        self._clients = [
            (p, OpenAI(base_url=p.base_url, api_key=p.api_key, timeout=60, max_retries=0))
            for p in providers
        ]

    def chat(self, messages: list[dict]) -> dict:
        for provider, client in self._clients:
            try:
                response = client.chat.completions.create(
                    model=provider.model,
                    messages=messages,
                )
                content = response.choices[0].message.content or ""
                return {"role": "assistant", "content": content}
            except SWITCH_PROVIDER as err:
                last_error = err
                log.warning("Provider %s failed (%s); trying next.", provider.name, type(err).__name__)
        raise RuntimeError("ALL LLM providers failed.") from last_error