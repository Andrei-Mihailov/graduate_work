from flask import Flask
from flask_jwt_extended import JWTManager
from passlib.context import CryptContext
from pydantic_settings import BaseSettings
from sentry_sdk import capture_exception, capture_message


class AuthJWT(BaseSettings):
    secret_key: str = "secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 20 * 60
    refresh_token_expire_minutes: int = 30 * 24 * 60 * 60  # 30 days


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


settings = Settings()


def configure_app(app: Flask):
    try:
        app.config["JWT_SECRET_KEY"] = settings.auth_jwt.secret_key
        app.config["JWT_ALGORITHM"] = settings.auth_jwt.algorithm
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.auth_jwt.access_token_expire_minutes
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.auth_jwt.refresh_token_expire_minutes

        jwt = JWTManager(app)
        capture_message("JWTManager configured successfully")
        return jwt
    except Exception as e:
        capture_exception(f"Error configuring JWTManager: {e}")
        raise
