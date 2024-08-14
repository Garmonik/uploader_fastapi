from pydantic_settings import BaseSettings
import logging
import sys
from logging import StreamHandler, Formatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(funcName)s -- %(message)s'))
logger.addHandler(handler)


# Connecting environment variables
class Settings(BaseSettings):
    DB_NAME: str = 'db'
    DB_USER: str = 'brainfeed'
    DB_PASS: str = 'BRAINfeed~1'
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 5432
    DB_DRIVER: str = 'postgresql'
    DB_URL: str = 'postgresql://brainfeed:BRAINfeed~1@127.0.0.1:5432/db'

    AWS_ACCESS_KEY_ID: str = ''
    AWS_SECRET_ACCESS_KEY: str = ''
    S3_ENDPOINT_URL: str = 'https://storage.yandexcloud.net'

    TIMEZONE: str = 'UTC'

    class Config:
        env_file = ".env"


settings = Settings()

