FROM python:3.9-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./ugc/api/requirements.txt requirements.txt

RUN apt-get update && apt-get -y install curl
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ugc/api/src .

COPY ./ugc/api/support/wait-services.sh .
RUN chmod +x wait-services.sh

CMD gunicorn --worker-class gevent \
    --workers $WORKERS \
    --bind 0.0.0.0:$PORT_APP \
    wsgi_app:app