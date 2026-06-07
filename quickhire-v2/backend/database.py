from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from pathlib import Path
import os

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "quickhire.db"

os.makedirs(DATA_DIR, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    # Add new columns if they don't exist (SQLite ALTER TABLE migration)
    with engine.connect() as conn:
        for col, dtype in [
            ("job_preference", "VARCHAR(200)"),
            ("city", "VARCHAR(100)"),
            ("target_city", "VARCHAR(100)"),
        ]:
            try:
                conn.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
            except Exception:
                pass  # column already exists
        conn.commit()
