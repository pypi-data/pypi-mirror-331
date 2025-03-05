import os
from pathlib import Path

from dotenv import load_dotenv

from shared_libraries.core.logger.create_logger import logger
from shared_libraries.environment.envs.environment import BaseEnvironment


class LocalEnvironment(BaseEnvironment):

    def __init__(self) -> None:
        super().__init__()
        self._load()

    def _load(self) -> None:
        dotenv_path = self._get_dotenv_path()
        load_dotenv(dotenv_path=dotenv_path,
                    override=True)
        # self._update_environment_variables()
        logger.info(msg="Loaded Local Environment")

    def get_environment_variable(self,
                                 key: str,
                                 default=None) -> str:
        return os.getenv(key=key,
                         default=default)

    @staticmethod
    def _get_dotenv_path(root_dir: str = "babylon") -> Path:
        current_path = Path.cwd().resolve()

        for path in [current_path] + list(current_path.parents):
            dotenv_path = path / ".env"
            if dotenv_path.exists() and dotenv_path.is_file():
                return dotenv_path

            if path.name.lower() == root_dir:
                dotenv_path = path / "BUILD" / ".env"
                return dotenv_path

        raise FileNotFoundError(f".env file is missing")

    @staticmethod
    def _update_environment_variables() -> None:
        host = "localhost"
        os.environ["BABYLON_DOCKER_HOST"] = host

        os.environ["REDIS_HOST"] = host
        os.environ["REDIS_PORT"] = os.getenv("REDIS_EXTERNAL_PORT", f"{6379}")

        os.environ["FAST_API_SERVICE_HOST"] = host
        os.environ["FAST_API_PORT"] = os.getenv("FAST_API_EXTERNAL_PORT", f"{8000}")

        os.environ["SOLUTIONS_API_HOST"] = host
        os.environ["SOLUTIONS_API_PORT"] = os.getenv("SOLUTIONS_API_EXTERNAL_PORT", f"{28005}")

        os.environ["MONGO_HOST"] = host
        os.environ["MONGO_PORT"] = os.getenv("MONGO_EXTERNAL_PORT", f"{27017}")

        os.environ["POSTGRES_HOST"] = host
        os.environ["POSTGRES_PORT"] = os.getenv("POSTGRES_EXTERNAL_PORT", f"{5432}")

        os.environ["PROTECT_GRAPHQL_ENDPOINT"] = f"{False}"

        # os.environ["R2R_BASE_URL"] = "http://40.76.224.245:7272"

        os.environ["CONTROL_PLANE_INTERNAL_HOST"] = "127.0.0.1"
        os.environ["MESSAGE_QUEUE_INTERNAL_HOST"] = "127.0.0.1"
        os.environ["CONTROL_PLANE_HOST"] = "127.0.0.1"
        os.environ["MESSAGE_QUEUE_HOST"] = "127.0.0.1"
        os.environ["KAFKA_HOST"] = "127.0.0.1"
        os.environ["PHOENIX_HOST"] = "127.0.0.1"

        os.environ["NEO4J_HOST"] = "127.0.0.1"
