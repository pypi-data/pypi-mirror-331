import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, confloat
from pydantic_settings import BaseSettings

from shared_libraries.environment.enironemnt import Environment

app_dir: Path = Path(os.getcwd()).resolve()
root_dir: Path = app_dir.parent.resolve()


class CommonSettings(BaseSettings):
    """Base project settings"""
    # App Settings
    app_dir: Path = Field(default=app_dir)

    # Logging Settings
    log_level_app: str | int = Field(default="info")
    log_level_api: str | int = Field(default="info")
    log_level_celery: str | int = Field(default="info")

    # Redis Credentials
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default="")

    # Remote Redis Credentials
    remote_redis_host: str = Field(default="localhost")
    remote_redis_port: int = Field(default=6379)
    remote_redis_password: str = Field(default="")

    # MongoDB Credentials
    mongo_host: str = Field(default="mongodb")
    mongo_port: int = Field(default=27017)
    mongo_username: str = Field(default="root")
    mongo_password: str = Field(default="example")
    mongo_files_db_name: str = Field(default="babylon_files")
    mongo_files_collection_name: str = Field(default="files")
    mongo_graph_files_collection_name: str = Field(default="graph_files")
    mongo_graph_nodes_collection_name: str = Field(default="graph_nodes")
    mongo_docstore_db_name: str = Field(default="babylon_docstore")
    mongo_cache_db_name: str = Field(default="babylon_cache")
    mongo_agent_files_collection_name: str = Field(default="agent_files")

    # LLM Credentials
    deployment_name_3_5_turbo_8k: str = Field(default="gpt-35-turbo")
    deployment_name_3_5_turbo_16k: str = Field(default="gpt-35-turbo-16k")
    deployment_name_8k: str = Field(default="gpt-4-turbo-2024-04-09")
    deployment_name_32k: str = Field(default="gpt-4-32k-0613")
    deployment_name_128k: str = Field(default="gpt-4o-2024-11-20")
    deployment_name_4o: str = Field(default="gpt-4o-2024-11-20")
    deployment_name_4o_mini: str = Field(default="gpt-4o-mini-2024-07-18")
    deployment_name_gemini: str = Field(default="gemini-1.5-pro-latest")
    openai_api_version: str = Field(default="2024-10-21")
    openai_api_key: str = Field(default="7fb47e73ae374ac3914235b6b01d1242")
    google_gemini_api_key: str = Field(default="AIzaSyBLxmIjk_BCvArwEwJp8dEmCah-BRWuHBY")
    azure_endpoint: str = Field(default="https://ai-proxy.lab.epam.com")
    groq_api_key: str = Field(default="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")
    groq_endpoint: str = Field(default="https://api.groq.com")

    # LLM Temperatures
    temperature_open_ai_text: confloat(ge=0, le=1) = Field(default=0)
    temperature_open_ai_mm: confloat(ge=0, le=1) = Field(default=0)
    temperature_gemini_text: confloat(ge=0, le=1) = Field(default=0)
    temperature_gemini_mm: confloat(ge=0, le=1) = Field(default=0)
    temperature_llama: confloat(ge=0, le=1) = Field(default=0)
    temperature_sma: confloat(ge=0, le=1) = Field(default=0.1)
    temperature_iaa: confloat(ge=0, le=1) = Field(default=0.1)

    # RAG Base
    r2r_base_url: str = Field(alias="R2R_BASE_URL", default="http://40.76.224.245:7272")

    # Documents Storage
    doc_storage_base_url: str = Field(alias="DOC_STORAGE_URL", default="http://40.76.224.245:8000")
    doc_storage_username: str = Field(alias="DOC_STORAGE_USER", default="babylon_paperless")
    doc_storage_password: str = Field(alias="DOC_STORAGE_PASSWORD", default="AGxjI4XOF46g445SoIsy")

    class Config:
        validate_assignment = True

    @staticmethod
    def get_boolean_env_var(var_name: str,
                            default_value: bool) -> bool:
        value = os.getenv(var_name, str(default_value))
        boolean_env_var = True if value.lower() in ("true", "1", "t", "y", "yes") else False
        return boolean_env_var

    @staticmethod
    def get_int_env_var(var_name: str,
                        default_value: int) -> int:
        int_env_var = int(os.getenv(var_name, str(default_value)))
        return int_env_var

    @classmethod
    @lru_cache()
    def get_app_config(cls) -> "CommonSettings":
        environment = Environment()
        _app_config = cls()
        return _app_config


app_common_config = CommonSettings.get_app_config()
