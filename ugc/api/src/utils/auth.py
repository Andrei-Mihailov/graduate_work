import asyncio
from http import HTTPStatus

import aiohttp
import jwt
from config import settings
from flask import request
from flask_jwt_extended import jwt_required
from sentry_sdk import capture_exception
from utils.auth_config import settings as settings_auth
from werkzeug.exceptions import Forbidden, HTTPException, Unauthorized


def decode_jwt(
    jwt_token: str,
    private_key: str = settings_auth.auth_jwt.secret_key,
    algorithm: str = settings_auth.auth_jwt.algorithm,
):
    try:
        decoded = jwt.decode(jwt_token, private_key, algorithms=[algorithm])
    except jwt.exceptions.DecodeError:
        raise Unauthorized(description="Invalid authentication credentials")
    except jwt.exceptions.InvalidAlgorithmError:
        raise Unauthorized(description="Invalid token algorithm")
    except jwt.exceptions.InvalidSignatureError:
        raise Unauthorized(description="Invalid token signature")
    except jwt.exceptions.ExpiredSignatureError:
        raise Unauthorized(description="Token has expired, refresh token")
    return decoded


class JWTBearer:
    def __init__(self, check_user: bool = False, auto_error: bool = True):
        self.check_user = check_user
        self.auto_error = auto_error

    def __call__(self, f):
        @jwt_required()
        def wrapper(*args, **kwargs):
            credentials = request.headers.get("Authorization")
            if not credentials:
                raise HTTPException(
                    description="Invalid authorization code.", code=Forbidden.code
                )
            if not credentials.startswith("Bearer "):
                raise HTTPException(
                    description="Only Bearer token might be accepted",
                    code=Unauthorized.code,
                )
            token = credentials.split()[1]
            decoded_token = self.parse_token(token)
            if not decoded_token:
                raise HTTPException(
                    description="Invalid or expired token.", code=Forbidden.code
                )

            if self.check_user:
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(
                    self.check(
                        settings.AUTH_API_ME_URL,
                        headers={"Authorization": f"Bearer {token}"},
                    )
                )
                if response.status != HTTPStatus.ACCEPTED:
                    raise HTTPException(
                        description="User doesn't exist", code=Forbidden.code
                    )

            return f(*args, **kwargs)

        return wrapper

    def parse_token(self, jwt_token: str) -> dict:
        try:
            return decode_jwt(jwt_token)
        except Exception as e:
            capture_exception(e)
            return {}

    @staticmethod
    async def check(
        query: str, params: dict = None, headers: dict = None, json: dict = None
    ):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if json is None:
            json = {}
        async with aiohttp.ClientSession(headers=headers) as client:
            try:
                async with client.get(query, json=json, params=params) as response:
                    return response
            except aiohttp.ClientError as e:
                capture_exception(e)
                raise


security_jwt = JWTBearer()
security_jwt_check = JWTBearer(check_user=True)
