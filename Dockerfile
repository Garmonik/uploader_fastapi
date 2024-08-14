FROM --platform=linux/amd64 python:3.11-slim-buster

WORKDIR /app

RUN python -m pip install pipenv
RUN set -ex && apt-get update

COPY ./app/Pipfile /app/Pipfile
COPY ./app/Pipfile.lock /app/Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile
RUN apt-get remove --auto-remove -y build-essential \
    && apt-get clean

COPY ./app ./

ENTRYPOINT ["uvicorn", "main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000

