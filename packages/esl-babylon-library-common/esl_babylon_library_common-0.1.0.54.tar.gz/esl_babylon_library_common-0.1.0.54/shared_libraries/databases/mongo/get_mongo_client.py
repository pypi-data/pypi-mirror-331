from pymongo import MongoClient

from shared_libraries.core.config import app_common_config


def get_mongo_client(host=app_common_config.mongo_host,
                     port=app_common_config.mongo_port,
                     username=app_common_config.mongo_username,
                     password=app_common_config.mongo_password) -> MongoClient:
    mongo_client = MongoClient(host=host,
                               port=port,
                               username=username,
                               password=password)
    return mongo_client
