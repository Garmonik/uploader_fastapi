import asyncio
import os
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, Request, Form, HTTPException, Header, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import Response, JSONResponse

from conf import logger
from database import get_db
from files_api.S3_storage import s3client
from files_api.models import FileInfo
from files_api.schemas import FileInfoResponse, FileDownloadResponse
from files_api.swagger import swagger_create_files_response, swagger_head_uuid_response, swagger_post_uuid_response, download_file_response
from files_api.utils import create_empty_file_in_db, is_number, get_file_format

FILE_DIR = 'files'

router = APIRouter(
    prefix='/api/files',
    tags=['files'])


@router.post("/create/", responses=swagger_create_files_response())
def create_file(request: Request, filename: str = Form(..., description="The name of the file to be created."), db: Session = Depends(get_db)):
    upload_length = request.headers.get("Upload-Length")
    if upload_length is None and is_number(upload_length):
        logger.debug('Upload-Length was not sent in the request or Upload-Length is not a number')
        raise HTTPException(status_code=400, detail="Upload-Length header is required or Upload-Length is not a number.")
    if filename is None:
        logger.debug('filename was not sent in the request')
        raise HTTPException(status_code=400, detail="filename is required.")

    logger.debug(f'Initializing file download {filename} of size {upload_length}')
    file_extension = os.path.splitext(filename)[1]
    file_uid = str(uuid.uuid4())
    save_as = str(uuid.uuid4()) + file_extension
    file_path = os.path.join(FILE_DIR, save_as)
    open(file_path, "wb").close()
    logger.debug(f'An empty file was created in local storage {file_path}')

    create_empty_file_in_db(file_uid, filename, upload_length, file_extension, db)

    return JSONResponse(
        status_code=200,
        content={
            "file_path": save_as
        }
    )


@router.head("/upload/{file_id}/", responses=swagger_head_uuid_response())
async def get_file_info(file_id: str):
    file_path = os.path.join(FILE_DIR, file_id)
    if not os.path.exists(file_path):
        logger.debug(f'file_id = {file_id}, {file_path} not fount')
        raise HTTPException(status_code=404, detail="File not found")
    file_size = os.path.getsize(file_path)
    return Response(headers={"Upload-Offset": str(file_size)})


@router.post("/upload/{file_id}/", responses=swagger_post_uuid_response())
async def upload_chunk(file_id: str, request: Request, chunk: UploadFile = File(...), upload_offset: int = Header(...), db: Session = Depends(get_db)):
    file_path = os.path.join(FILE_DIR, file_id)

    if not os.path.exists(file_path):
        logger.debug(f'file_id = {file_id}, {file_path} not fount')
        raise HTTPException(status_code=404, detail="File not found")
    if upload_offset is None:
        logger.debug(f'file_id = {file_id}, Upload-Offset header is missing')
        raise HTTPException(status_code=400, detail="Upload-Offset header is missing")

    try:
        upload_offset = int(upload_offset)
    except ValueError:
        logger.debug(f'file_id = {file_id}, upload_offset = {upload_offset}, Invalid Upload-Offset header value')
        raise HTTPException(status_code=400, detail="Invalid Upload-Offset header value")

    body = await chunk.read()
    logger.debug(f'Writing a new chunk to a local copy of the file')
    with open(file_path, "r+b") as f:
        f.seek(upload_offset)
        f.write(body)
    current_offset = upload_offset + len(body)

    upload_length = request.headers.get("Upload-Length")
    # Check if this is the last part of the file
    if upload_length:
        upload_length = int(upload_length)
        if current_offset >= upload_length:
            format_file = get_file_format(file_path)
            logger.debug(f'Uploading a file to cloud storage')
            asyncio.create_task(s3client.upload(db, format_file, file_path, file_id))

            return JSONResponse(
                status_code=201,
                content={
                    'file_id': file_id,
                    'uploaded': False,
                    'current_offset': current_offset
                },
            )
    return JSONResponse(status_code=200, content={"operation": "upload", "file_id": file_id, "current_offset": current_offset}, headers={"Upload-Offset": str(current_offset)})


@router.get("/list/", response_model=list[FileInfoResponse])
def get_files(skip: int = Query(0), limit: int = Query(10), db: Session = Depends(get_db)):
    # Request for selecting files taking into account the limit and offset
    files_query = select(FileInfo).offset(skip).limit(limit)
    result = db.execute(files_query).scalars().all()

    # Convert the result to a list
    file_list = [
        FileInfoResponse(
            id=file.id,
            original_name=file.original_name,
            size=file.size,
            format=file.format,
            uploaded=file.uploaded,
        ) for file in result
    ]

    return file_list


@router.get("/{file_id}/", responses=download_file_response())
async def download_file(file_id: str, db: Session = Depends(get_db)):
    """API method for receiving a file by UID with the ability to download."""

    # Checking the UUID format for correctness
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Incorrect file_id format")

    file_info = db.query(FileInfo).filter(FileInfo.id == file_uuid).first()
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found in database")
    if not file_info.uploaded:
        raise HTTPException(status_code=400, detail="The file is in the process of being uploaded to cloud storage")

    # Generating a key to access S3
    key = f"{file_info.id}.{file_info.extension}"

    try:
        # Receiving a file from S3
        signed_url = await s3client.get_signed_url(key=key)
    except:
        raise HTTPException(status_code=404, detail="File not found in cloud storage")
    file_list = FileDownloadResponse(
            id=file_info.id,
            original_name=file_info.original_name,
            size=file_info.size,
            format=file_info.format,
            uploaded=file_info.uploaded,
            download_url=signed_url
        )
    return JSONResponse(file_list, status_code=200)
