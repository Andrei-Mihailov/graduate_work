import pytest_asyncio
import aiohttp


@pytest_asyncio.fixture()
def make_post_request():
    async def inner(url: str, param: dict = None, cookie=None):
        async with aiohttp.ClientSession(cookies=cookie) as session:
            response = await session.post(url, params=param)
            return response

    return inner


@pytest_asyncio.fixture()
def make_put_request():
    async def inner(url: str, param: dict = None, cookie=None):
        async with aiohttp.ClientSession(cookies=cookie) as session:
            response = await session.put(url, params=param)
            return response

    return inner


@pytest_asyncio.fixture()
def make_get_request():
    async def inner(url: str, cookie=None):
        async with aiohttp.ClientSession(cookies=cookie) as session:
            response = await session.get(url)
            return response

    return inner
