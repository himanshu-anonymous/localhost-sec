"""
PostgreSQL Persistence Layer for localhost (BASTION X).
Handles connection pooling, engine management, session factory, and table initialisation.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import StaticPool

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
POSTGRES_DB = os.getenv("POSTGRES_DB", "localhost_db")

DEFAULT_DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

try:
    if "sqlite" in DATABASE_URL:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2}
        )
except Exception:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Local memory fallback engine when postgres is offline during tests/boot
_fallback_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)
_FallbackSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_fallback_engine)


def get_db():
    """FastAPI dependency yielding database session with resilient fallback."""
    try:
        db = SessionLocal()
        # Test connection quickly
        db.connection()
        try:
            yield db
        finally:
            db.close()
    except (OperationalError, Exception):
        # Fallback to local memory SQLite session
        Base.metadata.create_all(bind=_fallback_engine)
        db = _FallbackSessionLocal()
        try:
            yield db
        finally:
            db.close()


def init_db(target_engine=None):
    """Initialises all declared tables on target engine (defaults to global engine)."""
    e = target_engine or engine
    try:
        Base.metadata.create_all(bind=e)
    except Exception as exc:
        print(f"[Warning] Failed to initialize tables on {e.url}: {exc}")
        Base.metadata.create_all(bind=_fallback_engine)
