import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

IN_MEMORY = os.getenv("KIFAYAT_IN_MEMORY", "").lower() in ("1", "true", "yes")

if IN_MEMORY:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
else:
    from .config import DB_PATH
    engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
