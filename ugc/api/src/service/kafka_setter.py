from http import HTTPStatus
from http.client import HTTPException

import sentry_sdk
from backoff import expo, on_exception
from config import logger, settings
from kafka3 import KafkaProducer
from kafka3.errors import KafkaConnectionError


@on_exception(expo, KafkaConnectionError, max_tries=5)
def process_load_kafka(key, value):
    producer = KafkaProducer(
        bootstrap_servers=[f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"],
        client_id="ugc",
    )
    try:
        producer.send(settings.KAFKA_TOPIC, value=value, key=key)
    except Exception as exc:
        logger.exception(exc)
        sentry_sdk.capture_exception(exc)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description=str(exc))
    finally:
        producer.close()
