from typing import Protocol

import httpx

from eval_platform.models import EvaluationCase


class ProviderError(RuntimeError):
    """Raised when a model provider cannot produce output."""


class LLMProvider(Protocol):
    name: str

    async def generate(self, case: EvaluationCase) -> str:
        ...


class MockProvider:
    name = "mock"

    async def generate(self, case: EvaluationCase) -> str:
        if case.reference:
            return case.reference
        return f"Mock response for: {case.prompt}"


class OpenAICompatibleProvider:
    name = "openai-compatible"

    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 30) -> None:
        if not api_key or not model:
            raise ProviderError("API key and model are required for the OpenAI-compatible provider")
        self._endpoint = base_url.rstrip("/") + "/chat/completions"
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    async def generate(self, case: EvaluationCase) -> str:
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": case.prompt}],
            "temperature": 0,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    self._endpoint,
                    json=payload,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                response.raise_for_status()
                data = response.json()
            text = data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError("The model provider returned an invalid response") from exc
        if not isinstance(text, str) or not text.strip():
            raise ProviderError("The model provider returned empty output")
        return text.strip()