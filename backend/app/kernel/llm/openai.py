"""Provider LLM: OpenAI (cloud).

Menggunakan REST API OpenAI (`/v1/chat/completions`, `/v1/embeddings`).
"""

from __future__ import annotations

import httpx

from .base import ChatMessage, ChatResult, LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> ChatResult:
        payload: dict = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return ChatResult(
            content=content,
            model=self.model,
            provider=self.name,
            usage=data.get("usage", {}),
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/embeddings",
                json={"model": self.embedding_model, "input": texts},
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
        return [item["embedding"] for item in data["data"]]

    def is_available(self) -> bool:
        return bool(self.api_key)
