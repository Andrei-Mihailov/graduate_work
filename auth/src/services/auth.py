import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from db.postgres_db import get_session
from db.redis_db import RedisCache, get_redis

sentry_sdk.init("YOUR_SENTRY_DSN")  # Initialize Sentry SDK with your DSN

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    sentry_sdk.capture_exception(exc)
    return JSONResponse(status_code=422, content={"error": "Неверный запрос"})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    sentry_sdk.capture_exception(exc)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

class AuthService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = Authentication

    async def new_auth(self, auth_params) -> None:
        try:
            # добавление в бд pg данных об аутентификации модель Authentication
            await self.create_new_instance(auth_params)
        except Exception as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка создания новой аутентификации")

    async def login_history(
        self, access_token: str, limit: int = 10, page_number: int = 1
    ) -> list[Authentication]:
        try:
            payload = decode_jwt(jwt_token=access_token)
            user_uuid = payload.get("sub")
            # получить историю авторизаций по id_user_history модель Authentication
            auths_list = await self.get_login_history(
                user_uuid, limit=limit, offset=limit * (page_number - 1)
            )
            if auths_list is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
                )
            return auths_list
        except Exception as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка получения истории авторизаций")


@lru_cache()
def get_auth_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(redis, db)