from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings

def normalize_database_url(url: str) -> str:
    # Accept the common Supabase postgres:// URL as well as SQLAlchemy URLs.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url

database_url = normalize_database_url(settings.database_url)
is_sqlite = database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_options = {
    "pool_pre_ping": True,
    "connect_args": connect_args,
}
if not is_sqlite:
    # This application is a persistent FastAPI container using Supabase
    # session pooling (port 5432). Keep the app-side pool deliberately small.
    engine_options.update({
        "poolclass": QueuePool,
        "pool_size": 5,
        "max_overflow": 5,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    })

engine = create_engine(database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
