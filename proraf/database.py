from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from proraf.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Necessário para SQLite
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependência para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()