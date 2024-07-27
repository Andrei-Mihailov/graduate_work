FROM python:3.9-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY auth/requirements.txt requirements.txt
COPY auth/alembic.ini alembic.ini

RUN apt-get update
RUN pip install --no-cache-dir -r requirements.txt

COPY auth/src ./src