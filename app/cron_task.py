import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conf import settings
from files_api.models import FileInfo

# Setting up a database connection
DATABASE_URL = f"{settings.DB_DRIVER}://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?sslmode=disable"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def cleanup_old_files():
    """Removes old files from local disk based on the FileInfo model."""

    # get the current date and the date a week ago
    now = datetime.now()
    week_ago = now - timedelta(weeks=1)

    db = SessionLocal()

    try:
        # Retrieving all files created more than one week ago
        old_files = db.query(FileInfo).filter(FileInfo.created < week_ago).all()

        for file_info in old_files:
            # Forming the file name
            filename = f"./files/{file_info.id}.{file_info.extension}"

            # Check if the file exists, and if so, delete it
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Deleted file: {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_old_files()
