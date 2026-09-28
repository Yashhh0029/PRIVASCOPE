from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# Engine configuration for both SQLite (dev) and PostgreSQL (prod)
db_url = settings.normalized_database_url
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize database tables for local development/testing with idempotent column additions."""
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if 'users' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('users')}
        with engine.begin() as conn:
            if 'is_active' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
            if 'last_login_at' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME"))
