import logging
import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from routers import promocode, root
from middleware import sentry_exception_middleware
from db.postgres_db import engine
from models.base import Base

sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

sentry_sdk.init(
    dsn="https://7e322a912461958b85dcdf23716aeff5@o4507457845592064.ingest.de.sentry.io/4507457848016976",
    integrations=[sentry_logging],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.middleware("http")(sentry_exception_middleware)

app.add_middleware(SentryAsgiMiddleware)


app.include_router(promocode.router)
app.include_router(root.router)
