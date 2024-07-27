FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get -y install \
    build-essential \
    && apt-get clean

COPY ../../requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ../../src /app/src
COPY .. /app/tests

CMD ["pytest", "tests/test.py", "--maxfail=1", "--disable-warnings", "-v"]
