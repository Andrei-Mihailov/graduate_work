import json

from celery import Celery
from .message_sender import SendMessageManager


def init_celery() -> Celery:
    redis_url = "redis://redis"
    return Celery("tasks", broker=redis_url, backend=redis_url)


app = init_celery()


@app.task
def send(body) -> None:
    body_decode = body.decode("utf-8")
    message = json.loads(body_decode)

    manager = SendMessageManager()
    manager.send(message)
