import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, Base
from .kernel.config import settings
from .routers import projects, drawings, analysis, boq, export

# Buat semua tabel jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistem analisis perubahan gambar teknik konstruksi & estimasi dampak biaya deterministik.",
)

# CORS Middleware — allowlist dari env CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mounting untuk visualisasi gambar diff dan crops
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
app.mount("/static/data", StaticFiles(directory=DATA_DIR), name="static_data")

# Include Routers
app.include_router(projects.router)
app.include_router(drawings.router)
app.include_router(analysis.router)
app.include_router(boq.router)
app.include_router(export.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Construction Change Intelligence API"}
