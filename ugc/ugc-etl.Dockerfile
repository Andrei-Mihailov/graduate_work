FROM python:3.9-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./ugc/etl/requirements.txt requirements.txt

RUN apt-get update && apt-get -y install curl
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ugc/etl .

COPY ./ugc/etl/support/wait-services.sh .
RUN chmod +x wait-services.sh

CMD python main.py