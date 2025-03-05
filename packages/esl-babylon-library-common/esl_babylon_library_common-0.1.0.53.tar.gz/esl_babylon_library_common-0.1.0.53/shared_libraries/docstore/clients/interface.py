from abc import ABC, abstractmethod
from typing import Optional

from shared_libraries.docstore.schemas import Enterprise


class StorageClient(ABC):
    @abstractmethod
    def get_enterprise(self, enterprise_id: int) -> Optional[Enterprise]:
        raise NotImplementedError

    @abstractmethod
    def create_enterprise(self, enterprise_id: int) -> Optional[Enterprise]:
        raise NotImplementedError

    # @abstractmethod
    # def create_enterprise(self, name: str, path: str, match: str = "", matching_algorithm: int = 0,
    #                         is_insensitive: bool = False, owner: Optional[int] = None,
    #                         set_permissions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    #     raise NotImplementedError

    # @abstractmethod
    # def get_or_enterprise(self, name: str, path: str, match: str = "", matching_algorithm: int = 0,
    #                                is_insensitive: bool = False, owner: Optional[int] = None,
    #                                set_permissions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    #     raise NotImplementedError

    # @abstractmethod
    # def get_storage_path_by_id(self, storage_path_id: int) -> Optional[Dict[str, Any]]:
    #     pass
