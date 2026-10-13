"""Koneksi & helper antrean job (ARQ + Redis).

Hanya diimpor saat `jobs_enabled=true` (jalur async), agar proses web tidak
bergantung pada Redis ketika job dimatikan.
"""

from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from ..config import settings

_pool: ArqRedis | None = None


def redis_settings() -> RedisSettings:
    """Baca RedisSettings dari `settings.redis_url`."""
    return RedisSettings.from_dsn(settings.redis_url)


async def get_redis_pool() -> ArqRedis:
    """Kembalikan pool koneksi ARQ (dibuat sekali, dipakai ulang)."""
    global _pool
    if _pool is None:
        _pool = await create_pool(redis_settings())
    return _pool


async def enqueue_job(function: str, *args) -> None:
    """Masukkan pemanggilan fungsi worker ke antrean ARQ."""
    pool = await get_redis_pool()
    await pool.enqueue_job(function, *args)
