from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase



engine = create_engine(settings.database_url)

SessionLocal =sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass