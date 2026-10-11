import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default ke SQLite lokal, dapat di-override lewat env variable DATABASE_URL
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "construction.db"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
