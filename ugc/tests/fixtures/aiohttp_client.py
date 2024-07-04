import pytest
from aiohttp import ClientSession
from pydantic import AnyUrl


@pytest.fixture
def make_post_request():
    async def inner(url: AnyUrl, request_body: bytes) -> tuple[any, int]:
        async with ClientSession() as session:
            async with session.post(url, json=request_body) as response:
                return await response.json(), response.status

    return inner
