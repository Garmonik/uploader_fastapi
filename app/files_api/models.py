from sqlalchemy import Column, Integer, String, Float, UUID, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileInfo(Base):
    __tablename__ = 'files'
    id = Column(UUID, primary_key=True, index=True)
    original_name = Column(String)
    size = Column(Float, nullable=True)
    format = Column(String, nullable=True)
    extension = Column(String, nullable=True)
    uploaded = Column(Boolean, default=False)
    created = Column(DateTime, server_default=func.now(), nullable=False)
