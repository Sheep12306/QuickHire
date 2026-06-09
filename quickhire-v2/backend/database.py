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
            ("role", "VARCHAR(20) DEFAULT 'user'"),
            ("banned_until", "DATETIME"),
            ("ban_reason", "VARCHAR(500)"),
            ("membership_type", "VARCHAR(20) DEFAULT 'free'"),
            ("membership_expires_at", "DATETIME"),
            ("must_change_password", "BOOLEAN DEFAULT 0"),
        ]:
            try:
                conn.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
            except Exception:
                pass  # column already exists

        # Fix existing rows with NULL membership_type
        try:
            conn.exec_driver_sql(
                "UPDATE users SET membership_type = 'free' WHERE membership_type IS NULL"
            )
        except Exception:
            pass

        # Seed default super_admin if none exists
        try:
            result = conn.exec_driver_sql(
                "SELECT id FROM users WHERE role = 'super_admin' LIMIT 1"
            ).fetchone()
            if result is None:
                from security import hash_password
                pwd = hash_password("admin123")
                conn.exec_driver_sql(
                    "INSERT INTO users (email, password_hash, display_name, role, is_active, must_change_password, membership_type) "
                    "VALUES (:email, :pwd, :name, :role, 1, 1, 'free')",
                    {"email": "admin@quickhire.local", "pwd": pwd, "name": "超级管理员", "role": "super_admin"},
                )
        except Exception as e:
            import logging
            logging.warning(f"init_db: could not seed admin user: {e}")

        conn.commit()
