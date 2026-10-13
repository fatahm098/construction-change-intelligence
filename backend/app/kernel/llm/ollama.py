"""Provider LLM: Ollama (lokal).

Menggunakan HTTP API Ollama (`/api/chat`, `/api/embed`). Cocok untuk
pengembangan lokal tanpa API key.
"""

from __future__ import annotations

import httpx

from .base import ChatMessage, ChatResult, LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        embedding_model: str,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.embedding_model = embedding_model
        self.timeout = timeout

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> ChatResult:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = data.get("message", {}).get("content", "")
        return ChatResult(
            content=content,
            model=self.model,
            provider=self.name,
            usage={
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
            },
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.embedding_model, "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()
        return data.get("embeddings", [])

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
