"""Redis Synchronous/Asynchronous Context Manager

Usage example:
from ... import RedisContextManager

manager = RedisContextManager(
        username=, password=, host=, port=
    )

async with manager as connection:
    await connection.set("name", "John Doe")
"""

try:
    import redis
except ImportError as error:
    raise error


class RedisContextManager:
    """Redis Synchronous/Asynchronous Context Manager Interface"""

    def __init__(self, password: str, host: str, port: int) -> None:
        self.__password = password
        self.__host = host
        self.__port = port
        self.__url = f"redis://:{self.__password}@{self.__host}:{self.__port}"
        # @NOTE about `__max_connections`: https://redis.io/docs/latest/develop/reference/clients/
        self.__max_connections = 10_000
        self.__pool = redis.ConnectionPool(max_connections=self.__max_connections).from_url(self.__url)
        self.__a_pool = redis.asyncio.ConnectionPool(max_connections=self.__max_connections).from_url(self.__url)
        self.__concrete_connection: redis.Redis | None = None
        self.__a_concrete_connection: redis.asyncio.Redis | None = None

    def __enter__(self):
        try:
            self.__concrete_connection = redis.Redis(connection_pool=self.__pool, decode_responses=True)
        except redis.exceptions.RedisError as e:
            raise e
        return self.__concrete_connection

    def __exit__(self, exc_type, exc, tb):
        try:
            self.__concrete_connection.close()
        except redis.exceptions.RedisError as e:
            raise e

    async def __aenter__(self):
        try:
            self.__a_concrete_connection = await redis.asyncio.Redis(connection_pool=self.__a_pool,
                                                                     decode_responses=True)
        except redis.exceptions.RedisError as e:
            raise e
        return self.__a_concrete_connection

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self.__a_concrete_connection.aclose()
        except redis.exceptions.RedisError as e:
            raise e
