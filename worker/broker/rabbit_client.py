import json

import pika
import pika.channel
from pika.exceptions import AMQPConnectionError
from backoff import on_exception, expo
from loguru import logger

from core.settings import settings
from db.postgres_db import create_or_update_user


@on_exception(expo, (ConnectionError, AMQPConnectionError), max_tries=10)
def rabbit_connect(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=settings.rabbit_host,
                port=settings.rabbit_port,
                credentials=pika.PlainCredentials(settings.rabbit_user, settings.rabbit_password),
            ))

    channel = connection.channel()
    channel.exchange_declare(exchange="main",
                             exchange_type="direct",
                             durable=True,
                             auto_delete=False
                             )
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        logger.info("Received message %", body)
        dict_user = json.loads(body.decode('utf-8'))
        create_or_update_user(uuid=dict_user['uuid'], email=dict_user['email'], is_active=dict_user['is_active'])

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    logger.info("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
