from fastapi import Request
import sentry_sdk

async def sentry_exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e
    return response
