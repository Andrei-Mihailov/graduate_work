import multiprocessing
import sentry_sdk
import gunicorn.app.base

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from contextlib import asynccontextmanager
from backoff import on_exception, expo

from core.config import settings
from api.v1 import promocode
from db import redis_db


@on_exception(expo, (ConnectionError), max_tries=10)
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    await redis_db.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title="Сервис лояльности",
    description="Реализует методы проверки доступных пользователю промокодов, применение промокодов, покупки с использованием промокода и отмену применения промокода",
    docs_url="/loyality/api/openapi",
    openapi_url="/loyality/api/openapi.json",
    default_response_class=ORJSONResponse,
)

sentry_sdk.init(
    dsn=settings.sentry_sdk_dns,
    traces_sample_rate=settings.sentry_traces_sample_rate,
    profiles_sample_rate=settings.sentry_profiles_sample_rate,
)


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


app.include_router(promocode.router, prefix="/loyality/api/v1/promocodes")

if __name__ == "__main__":
    options = {
        "bind": "%s:%s" % ("0.0.0.0", settings.service_port),
        "workers": number_of_workers(),
        "worker_class": "uvicorn.workers.UvicornWorker",
    }

    StandaloneApplication(app, options).run()
