import os

from shared_libraries.environment.envs.environment import BaseEnvironment


class AzureEnvironment(BaseEnvironment):

    def __init__(self) -> None:
        super().__init__()

    def _load(self) -> None:
        self._update_environment_variables()
        print("Loaded Azure Environment")

    def get_environment_variable(self,
                                 key: str,
                                 default=None) -> str:
        return os.getenv(key=key,
                         default=default)

    @staticmethod
    def _update_environment_variables() -> None:
        os.environ["PROTECT_GRAPHQL_ENDPOINT"] = f"{False}"
        os.environ["R2R_BASE_URL"] = "http://40.76.224.245:7272"
