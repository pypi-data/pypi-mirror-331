import os

from shared_libraries.environment.envs.azure import AzureEnvironment
from shared_libraries.environment.envs.environment import BaseEnvironment
from shared_libraries.environment.envs.local import LocalEnvironment
from shared_libraries.environment.envs.local_docker import LocalDockerEnvironment


class Environment:
    def __init__(self) -> None:
        self.environment = self._detect_environment()

    def _detect_environment(self) -> BaseEnvironment:
        env_type = os.getenv("ENV_TYPE",
                             "local")

        envs = {
            "local": LocalEnvironment,
            "local_docker": LocalDockerEnvironment,
            "azure": AzureEnvironment
        }

        if env_type not in envs:
            raise ValueError(f"Unknown environment type: {env_type}")

        environment = envs.get(env_type)()

        return environment

    def current_environment(self):
        return self.environment
