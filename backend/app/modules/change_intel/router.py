"""Router agregator untuk modul Change Intelligence.

Mengekspor `routers` — daftar (prefix, APIRouter) yang di-include oleh `main.py`.
Pendekatan ini menghindari masalah nested include_router yang tidak ter-flatten
otomatis oleh FastAPI.
"""

from ...routers import projects, drawings, analysis, boq, export

# Setiap router lama sudah punya prefix sendiri (/api/projects, /api/drawings, dll.)
# jadi tidak perlu prefix tambahan di main.py.
routers = [
    projects.router,
    drawings.router,
    analysis.router,
    boq.router,
    export.router,
]

__all__ = ["routers"]
