from uuid import UUID

from pydantic import BaseModel


class FileInfoResponse(BaseModel):
    id: UUID
    original_name: str
    size: float
    format: str
    uploaded: bool


class FileDownloadResponse(BaseModel):
    id: UUID
    original_name: str
    size: float
    format: str
    uploaded: bool
