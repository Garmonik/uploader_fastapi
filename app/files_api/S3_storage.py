import os
from uuid import UUID

import aioboto3
from sqlalchemy.orm import Session

from conf import settings
from files_api.models import FileInfo


class S3Client:
    """A client for interacting with Amazon S3 asynchronously."""

    def __init__(self):
        """Initialize the S3 client."""
        self.session = aioboto3.Session()

    async def upload(self, db: Session, format_file: str = None, filename: str = '', key: str = None, bucket_name: str = 'files'):
        """Upload a file to S3 asynchronously."""
        file_id, _ = os.path.splitext(key)
        try:
            uuid = UUID(file_id)
        except ValueError:
            raise ValueError("Invalid format file_id")

        # Upload a file to S3
        async with self.session.client(
                service_name='s3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ) as s3:
            await s3.upload_file(filename, bucket_name, key)

        # Updating a record in the database
        file_info = db.query(FileInfo).filter(FileInfo.id == uuid).first()
        if file_info:
            file_info.uploaded = True
            file_info.format = format_file
            db.commit()
        else:
            raise ValueError("Record not found in database")

    async def get_signed_url(self, key: str = None, bucket_name: str = 'files'):
        """Generate a temporary URL for accessing a file in S3 asynchronously."""
        async with self.session.client(
                service_name='s3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ) as s3:
            # Checking for object presence before generating URL
            await s3.head_object(Bucket=bucket_name, Key=key)
            return await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600  # URL будет действителен в течение 1 часа
            )


s3client = S3Client()
