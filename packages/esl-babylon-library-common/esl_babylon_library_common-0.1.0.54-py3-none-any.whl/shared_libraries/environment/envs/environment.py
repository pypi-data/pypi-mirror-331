from abc import ABC, abstractmethod
from typing import Any, Callable


class BaseEnvironment(ABC):
    @abstractmethod
    def _load(self) -> Any:
        """
        Abstract protected method to load environment variables.
        This method should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_environment_variable(self,
                                 key: str,
                                 default: Any = None) -> None:
        """
        Abstract method to get an environment variable.
        This method should be implemented by subclasses.
        """
        pass

    def _get_services(self) -> Any:
        """
        Protected method to retrieve services specific to the environment.
        This method can be implemented by subclasses.
        """
        pass

    def _execute_within_environment(self,
                                    task: Callable) -> Any:
        """
        Protected method to execute a task within the environment.
        This method can be implemented by subclasses.
        """
        pass
