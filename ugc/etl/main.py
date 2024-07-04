from http import HTTPStatus
from http.client import HTTPException
from requests.exceptions import ConnectionError
import json
from datetime import datetime

from kafka3 import KafkaConsumer
from clickhouse_driver import Client
from kafka3.errors import KafkaConnectionError, NoBrokersAvailable
from backoff import on_exception, expo

from config import settings, logger, ch, kafka
from mapping import event_mappings


collect_dict = {}


def kafka_json_deserializer(serialized):
    return json.loads(serialized)


def init_db():
    for item_dt in event_mappings.keys():
        attr_name = event_mappings[item_dt][0]
        attr_type = event_mappings[item_dt][1]
        order_by = event_mappings[item_dt][2]
        attr_str = ""
        for i in range(len(attr_name)):
            attr_str = attr_str + attr_name[i] + " " + attr_type[i]
            if i < len(attr_name) - 1:
                attr_str = attr_str + ","

        query = f"""
            CREATE TABLE IF NOT EXISTS {settings.CH_DATABASE}.{item_dt}
                (
                    {attr_str}
                )
                Engine=MergeTree()
            ORDER BY ({",".join(order_by)})
            """
        ch.execute_query(query, None)
        collect_dict[item_dt] = []


def load_data_to_clickhouse(batch):
    for message in batch:
        message_key_str = message.key.decode("utf-8")
        payload = message.value
        payload_required = event_mappings[message_key_str][0]
        payload_required_types = event_mappings[message_key_str][1]
        checked = True

        for item in payload_required:
            if not item in payload.keys():
                checked = False
                logger.error(f"Error when trying parse click event {payload}")

        if checked:
            data_tuple = ()
            for i in range(len(payload_required)):
                if payload_required_types[i] == "DateTime":
                    try:
                        date_column = datetime.strptime(
                            payload[payload_required[i]], "%Y-%m-%d %H:%M:%S"
                        )
                        data_tuple += (date_column,)
                    except:
                        logger.error(
                            f"Error when trying parse date {payload[payload_required[i]]}"
                        )
                else:
                    data_tuple += (payload[payload_required[i]],)

            exists_data = collect_dict[message_key_str]
            exists_data.append(data_tuple)
            collect_dict[message_key_str] = exists_data

    for message_key_str, exists_data in collect_dict.items():
        payload_required = event_mappings[message_key_str][0]
        try:
            query = (
                f"INSERT INTO {message_key_str} ({','.join(payload_required)}) VALUES"
            )
            ch.clickhouse_connect.execute(query, exists_data)
            collect_dict[message_key_str] = []
        except Exception as e:
            logger.error(f"Error when trying to write Clickhouse: {str(e)}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))


@on_exception(
    expo, (KafkaConnectionError, NoBrokersAvailable), max_tries=settings.MAX_TRIES
)
def etl():
    batch = []
    for message in kafka.kafka_connect:
        message_key_str = message.key.decode("utf-8")

        if message_key_str in event_mappings.keys():
            batch.append(message)

            if len(batch) > settings.MAX_RECORDS_PER_BATCH:
                load_data_to_clickhouse(batch)
                kafka.kafka_connect.commit()
                batch = []


@on_exception(
    expo,
    (KafkaConnectionError, NoBrokersAvailable, ConnectionError),
    max_tries=settings.MAX_TRIES,
)
def get_connections():
    ch.clickhouse_connect = Client(
        host=settings.CH_HOST,
        database=settings.CH_DATABASE,
        user=settings.CH_USER,
        password=settings.CH_PASSWORD,
    )
    kafka.kafka_connect = KafkaConsumer(
        settings.KAFKA_TOPIC,
        group_id=settings.KAFKA_GROUP,
        bootstrap_servers=[f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"],
        auto_offset_reset="earliest",
        value_deserializer=kafka_json_deserializer,
        enable_auto_commit=False,
    )


if __name__ == "__main__":
    try:
        get_connections()
        init_db()
        etl()
    except Exception as e:
        logger.error(f"Error when trying to consume: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    finally:
        if ch.clickhouse_connect:
            ch.clickhouse_connect.disconnect()
        if kafka.kafka_connect:
            kafka.kafka_connect.close()
