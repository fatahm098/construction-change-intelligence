"""Kernel jobs: antrean ARQ, tugas background, dan konfigurasi worker.

Dipakai oleh `app.modules.jobs` (endpoint antrean/status) dan oleh worker ARQ
(`arq app.kernel.jobs.worker.WorkerSettings`).
"""

from .queue import enqueue_job, get_redis_pool, redis_settings
from .tasks import run_analysis_job

__all__ = [
    "enqueue_job",
    "get_redis_pool",
    "redis_settings",
    "run_analysis_job",
]
