"""Structured JSON logging + request-id context (stdlib only).

Modul ini menyediakan:
- `setup_logging()`: memasang formatter JSON pada root logger (idempoten).
- `JsonFormatter`: formatter yang mengubah setiap `LogRecord` menjadi satu baris JSON.
- `RequestContextMiddleware`: middleware ASGI yang menyalurkan `X-Request-ID`
  (dari header masuk atau UUID baru) ke `contextvars` sehingga ikut tercatat di
  setiap log record, lalu mengembalikannya di header respons.

Tanpa dependensi eksternal: hanya `logging`, `json`, `contextvars`, `uuid`.
"""

from __future__ import annotations

import contextvars
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from ..config import settings

# ContextVar menyimpan request-id aktif untuk task/konteks saat ini.
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

# Atribut bawaan LogRecord yang tidak perlu dikeluarkan ulang sebagai `extra`.
_RESERVED_ATTRS: frozenset[str] = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
        "message",
        "asctime",
    }
)


def get_request_id() -> str | None:
    """Kembalikan request-id aktif (atau `None` bila di luar request)."""
    return request_id_var.get()


class RequestIdFilter(logging.Filter):
    """Menyisipkan request-id aktif ke setiap record (bila ada)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "request_id", None) is None:
            record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    """Formatter satu-baris JSON: timestamp, level, logger, message, + extra."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id

        # Sertakan field `extra` kustom (aman-serialisasi JSON).
        for key, value in record.__dict__.items():
            if (
                key in _RESERVED_ATTRS
                or key in payload
                or key == "request_id"
                or key.startswith("_")
            ):
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except (TypeError, ValueError):
                payload[key] = repr(value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


_HANDLER_MARKER = "_cci_json_handler"


def _build_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    setattr(handler, _HANDLER_MARKER, True)
    return handler


def setup_logging(
    level: str | int | None = None,
    json_output: bool | None = None,
) -> logging.Logger:
    """Pasang logging terstruktur pada root logger. Idempoten (aman dipanggil ulang).

    Bila `json_output` False, format teks biasa tetap dipakai (memudahkan dev).
    `level`/`json_output` default diambil dari `settings` (`LOG_LEVEL`, `LOG_JSON`).
    """
    resolved_level = level if level is not None else settings.log_level
    resolved_json = json_output if json_output is not None else settings.log_json

    root = logging.getLogger()

    handler: logging.Handler | None = None
    for existing in root.handlers:
        if getattr(existing, _HANDLER_MARKER, False):
            handler = existing
            break

    if handler is None:
        handler = _build_handler()
        root.addHandler(handler)

    # Selalu sinkronkan formatter/level (mendukung rekonfigurasi tanpa duplikasi).
    handler.setFormatter(JsonFormatter() if resolved_json else logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s"
    ))

    if isinstance(resolved_level, str):
        root.setLevel(resolved_level.upper())
    else:
        root.setLevel(resolved_level)

    # Kurangi bisingnya access log uvicorn agar tidak dobel dengan log kita.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root


class RequestContextMiddleware:
    """Middleware ASGI murni: propagasi `X-Request-ID` via contextvars + header respons."""

    def __init__(self, app: Any, header_name: str = "X-Request-ID") -> None:
        self.app = app
        self.header_name = header_name
        self._header_key = header_name.lower().encode("latin-1")

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._extract_request_id(scope)
        token = request_id_var.set(request_id)

        async def send_with_request_id(message: dict) -> None:
            if message.get("type") == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((self._header_key, request_id.encode("latin-1")))
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            request_id_var.reset(token)

    def _extract_request_id(self, scope: dict) -> str:
        for key, value in scope.get("headers") or []:
            if key.lower() == self._header_key:
                try:
                    candidate = value.decode("latin-1").strip()
                except Exception:  # noqa: BLE001
                    candidate = ""
                if candidate:
                    return candidate
                break
        return str(uuid.uuid4())
