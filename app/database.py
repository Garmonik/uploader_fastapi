from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conf import settings
from files_api.models import Base

# Setting up and connecting the database
DATABASE_URL = f"{settings.DB_DRIVER}://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?sslmode=disable"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
