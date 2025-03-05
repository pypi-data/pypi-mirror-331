from contextlib import asynccontextmanager, contextmanager
from typing import Generator, AsyncGenerator

import redis

from shared_libraries.databases.redis.get_redis_url import get_redis_url


def create_redis_session(decode_responses: bool,
                         is_remote: bool,
                         redis_db: int) -> redis.Redis:
    redis_url = get_redis_url(is_remote=is_remote,
                              redis_db=redis_db)
    redis_session = redis.from_url(url=redis_url,
                                   decode_responses=decode_responses)
    return redis_session


@contextmanager
def redis_iterator(is_remote: bool = False,
                   redis_db: int = 0) -> Generator[redis.Redis, None, None]:
    redis_session = create_redis_session(decode_responses=True,
                                         is_remote=is_remote,
                                         redis_db=redis_db)
    try:
        yield redis_session
    finally:
        redis_session.close()


def get_redis_session(is_remote: bool = False,
                      redis_db: int = 0) -> Generator[redis.Redis, None, None]:
    with redis_iterator(is_remote=is_remote,
                        redis_db=redis_db) as redis_session:
        yield redis_session


async def create_aredis_session(decode_responses: bool,
                                is_remote: bool,
                                redis_db: int) -> redis.asyncio.Redis:
    redis_url = get_redis_url(is_remote=is_remote,
                              redis_db=redis_db)
    redis_session = redis.asyncio.from_url(url=redis_url,
                                           decode_responses=decode_responses)
    return redis_session


@asynccontextmanager
async def aredis_iterator(is_remote: bool = False,
                          redis_db: int = 0) -> AsyncGenerator[redis.asyncio.Redis, None]:
    async_redis_session = await create_aredis_session(decode_responses=True,
                                                      is_remote=is_remote,
                                                      redis_db=redis_db)
    try:
        yield async_redis_session
    finally:
        await async_redis_session.aclose()


async def get_aredis_session(is_remote: bool = False,
                             redis_db: int = 0) -> AsyncGenerator[redis.asyncio.Redis, None]:
    async with aredis_iterator(is_remote=is_remote,
                               redis_db=redis_db) as redis_session:
        yield redis_session
