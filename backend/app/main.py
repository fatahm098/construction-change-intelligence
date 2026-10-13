import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import SessionLocal, engine, Base
from .kernel.config import settings
from .modules import get_module_routers

# Buat semua tabel jika belum ada
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Rehidrasi vector store in-memory dari DB (hilang setiap restart).
    from .models import AHSPItem
    from .modules.doc_qa.service import hydrate_vector_store
    from .services.ahsp_seed import seed_ahsp

    db = SessionLocal()
    try:
        loaded = hydrate_vector_store(db)
        if loaded:
            print(f"[startup] vector store dihidrasi: {loaded} chunk")

        # Seed katalog AHSP bila masih kosong (agar demo langsung jalan).
        if db.query(AHSPItem).count() == 0:
            seeded = seed_ahsp(db)
            print(f"[startup] katalog AHSP di-seed: {seeded} item")
    except Exception as e:  # noqa: BLE001
        print(f"[startup] gagal menyiapkan data awal: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistem analisis perubahan gambar teknik konstruksi & estimasi dampak biaya deterministik.",
    lifespan=lifespan,
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

# Include Routers (module registry)
for _router in get_module_routers():
    app.include_router(_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Construction Change Intelligence API"}
