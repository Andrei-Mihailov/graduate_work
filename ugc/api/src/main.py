import sentry_sdk
from api.v1.kafka_producer import ugc_blueprint
from backoff import expo, on_exception
from config import pg_config_data, settings
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from kafka3.admin import KafkaAdminClient, NewTopic
from kafka3.errors import KafkaConnectionError

app = Flask(__name__)
api = Api(app)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+asyncpg://{pg_config_data.user}:{pg_config_data.password}@{pg_config_data.host}:"
    f"{pg_config_data.port}/{pg_config_data.dbname}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
jwt = JWTManager(app)

app.register_blueprint(ugc_blueprint)

sentry_sdk.init(
    dsn="https://7e322a912461958b85dcdf23716aeff5@o4507457845592064.ingest.de.sentry.io/4507457848016976",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


@on_exception(expo, (KafkaConnectionError), max_tries=settings.MAX_TRIES)
def init_app():
    admin_client = KafkaAdminClient(
        bootstrap_servers=[f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"],
        client_id="ugc",
    )
    server_topics = admin_client.list_topics()
    if settings.KAFKA_TOPIC not in server_topics:
        new_topic_list = [
            NewTopic(
                name=settings.KAFKA_TOPIC,
                num_partitions=settings.NUM_PARTITIONS,
                replication_factor=settings.REPLICATION_FACTOR,
            )
        ]
        admin_client.create_topics(new_topics=new_topic_list, validate_only=False)

    admin_client.close()


@app.route("/")
def index():
    return "App start"


if __name__ == "__main__":
    init_app()
    app.run(debug=settings.DEBUG)
