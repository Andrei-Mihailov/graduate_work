import json
from datetime import datetime
from http import HTTPStatus

from config import logger
from flask import Blueprint, jsonify, request
from sentry_sdk import capture_message
from service.kafka_setter import process_load_kafka
from utils.auth import security_jwt_check

ugc_blueprint = Blueprint("ugc", __name__, url_prefix="/ugc")


# путь до ручки
# :5000/ugc/send-to-broker/movie_events?movie_id=1&user_id=12&user_fio=Ivanov_Ivan_Ivanovich&movie_name
# =Interstellar&fully_viewed=True
@ugc_blueprint.route("/send-to-broker/<type_event>", methods=["GET", "POST"])
def send_message_to_kafka(type_event: str):
    user = security_jwt_check(request)
    if not user:
        capture_message("Unauthorized access attempt.")
        return jsonify({"error": "Unauthorized"}), HTTPStatus.UNAUTHORIZED
    data = request.args.to_dict()
    if not data:
        capture_message("No data provided in the request.")
        return jsonify({"error": "Data is required"}), HTTPStatus.BAD_REQUEST

    data["date_event"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        capture_message(f"Sending message to Kafka with event type: {type_event} and data: {data}")
        process_load_kafka(key=type_event.encode(), value=json.dumps(data).encode())
        capture_message(f"Message sent to Kafka successfully for event type: {type_event}")
        return jsonify({"status": "Message sent to Kafka"}), HTTPStatus.OK
    except Exception as e:
        capture_message("Failed to send message to Kafka.")
        logger.exception(e)
        return jsonify({"status": "Error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR
