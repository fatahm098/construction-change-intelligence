"""Abstraksi provider LLM.

Semua provider harus mengimplementasikan `LLMProvider`. Ini memungkinkan
penukaran provider (deepseek/openai/ollama) tanpa mengubah kode pemanggil.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class ChatResult:
    content: str
    model: str
    provider: str
    usage: dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Antarmuka provider LLM."""

    name: str = "base"

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> ChatResult:
        """Kirim percakapan, kembalikan respons teks."""
        raise NotImplementedError

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Kembalikan vektor embedding untuk setiap teks."""
        raise NotImplementedError

    def structured_extract(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """Ekstraksi terstruktur mengikuti JSON schema.

        Implementasi default: minta model mengembalikan JSON, lalu parse.
        Provider yang mendukung function/tool calling boleh meng-override.
        """
        import json

        system = (
            "Kamu adalah asisten ekstraksi data teknik sipil. "
            "Balas HANYA dengan JSON valid yang mengikuti skema, tanpa penjelasan tambahan."
        )
        schema_hint = f"Skema JSON yang wajib diikuti:\n{json.dumps(schema, ensure_ascii=False)}"
        result = self.chat(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=f"{prompt}\n\n{schema_hint}"),
            ],
            temperature=temperature,
        )
        text = result.content.strip()
        # Buang code fence jika ada
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)

    def is_available(self) -> bool:
        """Cek apakah provider siap dipakai (mis. server hidup / API key ada)."""
        return True
