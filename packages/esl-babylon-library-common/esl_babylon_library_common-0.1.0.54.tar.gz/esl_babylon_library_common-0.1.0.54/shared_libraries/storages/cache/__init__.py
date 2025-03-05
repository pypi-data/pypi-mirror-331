from shared_libraries.core.config import app_common_config
from shared_libraries.storages.cache.manager import RedisContextManager

redis_async_manager = RedisContextManager(
    password=app_common_config.remote_redis_password,
    host=app_common_config.remote_redis_host,
    port=app_common_config.remote_redis_port,
)
