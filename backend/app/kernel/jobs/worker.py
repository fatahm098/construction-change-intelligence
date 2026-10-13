"""Konfigurasi worker ARQ.

Jalankan worker dengan:
    arq app.kernel.jobs.worker.WorkerSettings
"""

from arq.connections import RedisSettings

from ..config import settings
from .tasks import run_analysis_job


class WorkerSettings:
    """Didaftarkan sebagai entrypoint worker ARQ."""

    functions = [run_analysis_job]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 1          # analisis berat & CPU-bound → satu per worker
    job_timeout = 900     # 15 menit
    keep_result = 3600    # simpan hasil 1 jam
