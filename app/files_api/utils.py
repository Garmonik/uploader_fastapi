import uuid

import magic
from sqlalchemy.orm import Session

from conf import logger
from files_api.models import FileInfo


def get_file_format(filename):
    try:
        return magic.from_file(filename, mime=True)
    except:
        logger.debug(f'Failed to get file format')
        return None


def create_empty_file_in_db(file_uid: str, filename: str, upload_length: str, file_extension: str, db: Session):
    new_file = FileInfo(
        id=uuid.UUID(file_uid),
        original_name=filename,
        size=float(upload_length),
        format=None,
        extension=file_extension,
        uploaded=False
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    logger.debug(f'A record has been created in the database with id = {file_uid}')


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
