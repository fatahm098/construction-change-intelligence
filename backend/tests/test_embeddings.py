"""Test provider embedding (hash + OpenAI-compatible) dan endpoint reindex."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.kernel.config import settings
from app.kernel.llm.embedding import (
    HashEmbeddingProvider,
    OpenAICompatibleEmbeddingProvider,
    get_embedding_provider,
)
from app.kernel.rag.embedder import Embedder
from app.main import app

client = TestClient(app)


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def json(self) -> dict:
        return self._payload


def _fake_post(calls: list, *, status_code: int = 200, reverse: bool = True):
    """Ganti httpx.Client.post; respons sengaja tidak berurutan."""

    def post(self, url, *, json, headers, **kwargs):
        calls.append({"url": url, "json": json, "headers": headers})
        count = len(json["input"])
        order = range(count - 1, -1, -1) if reverse else range(count)
        data = [{"index": i, "embedding": [float(i), 0.5]} for i in order]
        return _FakeResponse({"data": data}, status_code=status_code)

    return post


# --- Hash provider -----------------------------------------------------------


def test_hash_provider_deterministic_and_consistent_dimensions():
    provider = HashEmbeddingProvider()

    first = provider.embed(["kuat tekan beton fc' 24,9 MPa"])
    second = provider.embed(["kuat tekan beton fc' 24,9 MPa"])

    assert first == second
    assert len(first) == 1
    assert len(first[0]) == 512
    assert provider.dimensions == 512


def test_hash_provider_empty_input_returns_empty_list():
    assert HashEmbeddingProvider().embed([]) == []
    assert Embedder(HashEmbeddingProvider()).embed_texts([]) == []


# --- Factory -----------------------------------------------------------------


def test_factory_falls_back_to_hash(monkeypatch):
    monkeypatch.setattr(settings, "embedding_provider", "tidak-dikenal")
    assert isinstance(get_embedding_provider(), HashEmbeddingProvider)


def test_factory_openai_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "embedding_provider", "openai")
    monkeypatch.setattr(settings, "embedding_api_key", None)
    monkeypatch.setattr(settings, "openai_api_key", None)

    with pytest.raises(RuntimeError, match="EMBEDDING_API_KEY"):
        get_embedding_provider()


# --- OpenAI-compatible provider ---------------------------------------------


def test_openai_provider_request_and_index_order(monkeypatch):
    calls: list = []
    monkeypatch.setattr(httpx.Client, "post", _fake_post(calls))

    provider = OpenAICompatibleEmbeddingProvider(
        api_key="sk-rahasia",
        model="text-embedding-3-small",
        base_url="https://llm.example/v1/",
    )
    vectors = provider.embed(["a", "b", "c"])

    assert len(calls) == 1
    assert calls[0]["url"] == "https://llm.example/v1/embeddings"
    assert calls[0]["headers"]["Authorization"] == "Bearer sk-rahasia"
    assert calls[0]["json"] == {
        "model": "text-embedding-3-small",
        "input": ["a", "b", "c"],
    }
    # Respons datang terbalik (index 2,1,0) → hasil harus urut sesuai input.
    assert vectors == [[0.0, 0.5], [1.0, 0.5], [2.0, 0.5]]


def test_openai_provider_batches_max_64(monkeypatch):
    calls: list = []
    monkeypatch.setattr(httpx.Client, "post", _fake_post(calls, reverse=False))

    provider = OpenAICompatibleEmbeddingProvider(api_key="k")
    vectors = provider.embed([f"teks-{i}" for i in range(65)])

    assert [len(call["json"]["input"]) for call in calls] == [64, 1]
    assert len(vectors) == 65


def test_openai_provider_error_mentions_endpoint_without_api_key(monkeypatch):
    calls: list = []
    monkeypatch.setattr(httpx.Client, "post", _fake_post(calls, status_code=401))

    provider = OpenAICompatibleEmbeddingProvider(
        api_key="sk-rahasia",
        model="model-uji",
        base_url="https://llm.example/v1",
    )

    with pytest.raises(RuntimeError) as excinfo:
        provider.embed(["x"])

    message = str(excinfo.value)
    assert "https://llm.example/v1" in message
    assert "model-uji" in message
    assert "sk-rahasia" not in message


# --- Reindex endpoint --------------------------------------------------------


def test_reindex_endpoint_on_empty_db(monkeypatch):
    monkeypatch.setattr(settings, "embedding_provider", "hash")

    res = client.post("/api/doc-qa/reindex")

    assert res.status_code == 200, res.text
    body = res.json()
    assert body["chunks"] == 0
    assert body["provider"] == "hash"
    assert body["dimensions"] == 512
