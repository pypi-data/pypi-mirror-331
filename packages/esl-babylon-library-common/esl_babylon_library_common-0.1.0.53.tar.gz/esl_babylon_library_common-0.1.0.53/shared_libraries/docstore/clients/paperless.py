import io
from pathlib import Path
from typing import Any, Dict, List, Union, Tuple

import requests

from shared_libraries.core.config import app_common_config
from shared_libraries.core.logger.create_logger import logger


class PaperlessClient:
    def __init__(self,
                 base_url: str = app_common_config.doc_storage_base_url,
                 username: str = app_common_config.doc_storage_username,
                 password: str = app_common_config.doc_storage_password):
        """
        Initialize the Paperless client.

        Arguments:
        base_url : str - Base URL of the Paperless service.
        username : str - Username for authentication.
        password : str - Password for authentication.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = self.obtain_token()
        self.storage_path_endpoint = "/api/storage_paths/"
        self.documents_endpoint = "/api/documents/"
        self.tags_endpoint = "/api/tags/"
        self.upload_endpoint = "/api/documents/post_document/"
        self.trash_endpoint = f"/trash/"
        self.download_path = Path.home() / "Downloads"

    def obtain_token(self) -> str:
        """
        Obtain an authentication token.

        Returns:
        str - Authentication token.
        """
        login_url = f"{self.base_url}/api/token/"
        credentials = {"username": self.username, "password": self.password}
        response = requests.post(login_url, data=credentials)
        response.raise_for_status()
        token = response.json().get("token")
        logger.info("Obtained authentication token.")
        return token

    def refresh_token(self) -> None:
        """
        Refresh the authentication token.
        """
        self.token = self.obtain_token()

    def _retry_request_on_unauthorized(self,
                                       method: str,
                                       url: str,
                                       headers: Dict[str, str],
                                       **kwargs: Any) -> Union[Dict[str, Any], None]:
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 401:
                self.refresh_token()
                headers['Authorization'] = f'Token {self.token}'
                response = requests.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.json()
            else:
                logger.error(f"HTTP error ({http_err.response.status_code}) at {url}: {http_err}")
                return None
        except Exception as err:
            logger.error(f"Unexpected error at {url}: {err}")
            return None

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], None]:
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Token {self.token}'
        logger.info(f"Making {method} request to {url} with params {kwargs}")
        return self._retry_request_on_unauthorized(method, url, headers, **kwargs)

    def _create_item(self, endpoint: str, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a new item (enterprise or tag).

        Arguments:
        endpoint : str - The API endpoint for the item.
        name : str - The name of the item.
        kwargs : Any - Additional arguments for the item creation.

        Returns:
        Dict[str, Any] - The created item data.
        """
        data = {'name': name}
        data.update(kwargs)
        response = self._request(method="POST", endpoint=endpoint, json=data)
        return response

    def _get_item(self, endpoint: str, name: str) -> Dict[str, Any] | None:
        """
        Get an item by its name.

        Arguments:
        endpoint : str - The API endpoint for the item.
        name : str - The name of the item.

        Returns:
        Dict[str, Any] | None - The item data if found, otherwise None.
        """
        response = self._request(method="GET", endpoint=endpoint)
        if response:
            results = response.get("results", [])
            for result in results:
                if result.get("name") == name:
                    return result
        return None

    def _get_or_create_item(self, endpoint: str, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Get or create an item (enterprise or tag).

        Arguments:
        endpoint : str - The API endpoint for the item.
        name : str - The name of the item.
        kwargs : Any - Additional arguments for the item creation.

        Returns:
        Dict[str, Any] - The created item data or existing item if it does not exist.
        """
        item = self._get_item(endpoint, name)
        if item is None:
            item = self._create_item(endpoint, name, **kwargs)
        return item

    def _list_items(self, endpoint: str) -> List[Dict[str, Any]]:
        """
        Get all items.

        Arguments:
        endpoint : str - The API endpoint for the item.

        Returns:
        List[Dict[str, Any]] - The list of items.
        """
        response = self._request(method="GET", endpoint=endpoint)
        if response:
            return response.get("results", [])
        return []

    def _get_download_path(self, file_name: str) -> Path:
        """
        Get the download path in the user's downloads directory.

        Arguments:
        file_name : str - The name of the file to be downloaded.

        Returns:
        Path - The path in the download directory.
        """
        self.download_path.mkdir(parents=True, exist_ok=True)
        return self.download_path / file_name

    @staticmethod
    def _save_document(response: requests.Response, save_path: Path) -> None:
        """
        Save the document from the response to the specified path.

        Arguments:
        response : requests.Response - The HTTP response containing the document.
        save_path : Path - The path to save the document.
        """
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        logger.info(f"Document successfully downloaded to {save_path}")

    def get_task_status(self, task_id: str) -> Dict[str, Any] | None:
        """
        Get the status of a task by its UUID.

        Arguments:
        task_id : str - UUID of the task.

        Returns:
        Dict[str, Any] | None - Response from the API in JSON format, or None if an error occurred.
        """
        try:
            endpoint = f"/api/tasks/?task_id={task_id}"
            return self._request(method="GET", endpoint=endpoint)
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            return None
        except Exception as err:
            logger.error(f"An error occurred during request: {err}")
            return None

    def create_enterprise_collection(self, enterprise_name: str) -> Dict[str, Any]:
        """
        Create a new enterprise collection (storage path).

        Arguments:
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        Dict[str, Any] - The created enterprise data collection.
        """
        return self._create_item(
            endpoint=self.storage_path_endpoint,
            name=enterprise_name,
            path=enterprise_name + "/{title}",
            match="",
            matching_algorithm=0,
            is_insensitive=False,
            owner=None,
            set_permissions={}
        )

    def get_enterprise_collection(self, enterprise_name: str) -> Dict[str, Any] | None:
        """
        Get the enterprise collection data (storage path) by enterprise_id.

        Arguments:
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        Dict[str, Any] | None - The enterprise data collection if found, otherwise None.
        """
        return self._get_item(endpoint=self.storage_path_endpoint, name=enterprise_name)

    def get_enterprise_collection_by_id(self, object_id: int) -> Dict[str, Any] | None:
        """
        Get an enterprise collection data by its ID.

        Arguments:
        object_id : int - The ID of the enterprise collection.

        Returns:
        Dict[str, Any] | None - The enterprise collection data if found, otherwise None.
        """
        return self._request("GET", f"{self.storage_path_endpoint}{object_id}/")

    def get_or_create_enterprise_collection(self, enterprise_name: str) -> Dict[str, Any]:
        """
        Get or create an enterprise collection (storage path).

        Arguments:
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        Dict[str, Any] - The created enterprise data collection or existing it if it does not exist.
        """
        return self._get_or_create_item(
            endpoint=self.storage_path_endpoint,
            name=enterprise_name,
            path=enterprise_name + "/{title}",
            match="",
            matching_algorithm=0,
            is_insensitive=False,
            owner=None,
            set_permissions={}
        )

    def list_enterprise_collections(self) -> List[Dict[str, Any]]:
        """
        Get all enterprise collections (storage paths).

        Returns:
        List[Dict[str, Any]] - The list of enterprise collections.
        """
        return self._list_items(endpoint=self.storage_path_endpoint)

    def create_agent_tag(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a new agent tag.

        Arguments:
        name : str - The name of the agent tag.
        kwargs : Any - Additional arguments for the agent tag creation.

        Returns:
        Dict[str, Any] - The created agent tag data.
        """
        return self._create_item(endpoint=self.tags_endpoint, name=name, **kwargs)

    def get_agent_tag(self, name: str) -> Dict[str, Any] | None:
        """
        Get an agent tag by its name.

        Arguments:
        name : str - The name of the agent tag.

        Returns:
        Dict[str, Any] | None - The agent tag data if found, otherwise None.
        """
        return self._get_item(endpoint=self.tags_endpoint, name=name)

    def get_agent_tag_by_id(self, object_id: int) -> Dict[str, Any] | None:
        """
        Get an agent tag data by its ID.

        Arguments:
        object_id : int - The ID of the agent tag.

        Returns:
        Dict[str, Any] | None - The agent tag data if found, otherwise None.
        """
        return self._request(method="GET", endpoint=f"{self.tags_endpoint}{object_id}/")

    def get_or_create_agent_tag(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Get or create an agent tag.

        Arguments:
        name : str - The name of the agent tag.
        kwargs : Any - Additional arguments for the agent tag creation.

        Returns:
        Dict[str, Any] - The created agent tag data or existing agent tag if it does not exist.
        """
        return self._get_or_create_item(endpoint=self.tags_endpoint, name=name, **kwargs)

    def list_agent_tags(self) -> List[Dict[str, Any]]:
        """
        Get all agent tags.

        Returns:
        List[Dict[str, Any]] - The list of agent tags.
        """
        return self._list_items(endpoint=self.tags_endpoint)

    def search_documents(self,
                         filename: str = "",
                         enterprise_name: str = "",
                         agent_names: List[str] | None = None) -> Dict[str, Any]:
        """
        Search for documents based on various filters.

        Arguments:
        filename : str - The filename to search for.
        enterprise_name : str - The name of the enterprise.
        agent_names : List[str] | None - The list of agent names.

        Returns:
        Dict[str, Any] - The search results from the API.
        """
        queries = []
        if enterprise_name:
            queries.append(f"path:{enterprise_name}")

        if filename:
            queries.append(f"original_filename:{filename}")

        if agent_names:
            if len(agent_names) == 1:
                queries.append(f"tag:{agent_names[0]}")
            else:
                tag_query = " AND ".join([f"tag:{tag}" for tag in agent_names])
                queries.append(tag_query)

        query = " ".join(queries)
        params = {"query": query} if query else {}
        logger.info(f"Requesting documents metadata with filters: {params}")
        response = self._request(method="GET", endpoint=self.documents_endpoint, params=params)
        return response if response else {}

    def get_document_name(self, document_id: int) -> str:
        """
        Get the name of the document from the Paperless service.

        Arguments:
        document_id : int - ID of the document.

        Returns:
        str - The name of the document.
        """
        document = self._request("GET", f"/api/documents/{document_id}/")
        return document.get("original_file_name", f"document_{document_id}")

    def upload_document(self, file_path: str,
                        enterprise_name: str,
                        agent_tag_names: List[str] | None = None) -> Any:
        """
        Upload a document to the Paperless service.

        Arguments:
        file_path : str - Path to the document file to upload.
        enterprise_name : str - The name of the enterprise.
        agent_tag_names : List[str] | None - List of agent tags names.

        Returns:
        Any - Response from the API in JSON format.
        """
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name
        enterprise_data = self.get_or_create_enterprise_collection(enterprise_name)
        agent_tag_ids = []
        if agent_tag_names:
            for agent_tag_name in agent_tag_names:
                agent_tag = self.get_or_create_agent_tag(agent_tag_name)
                agent_tag_ids.append(agent_tag.get("id"))

        logger.info(f"Uploading {file_name} to enterprise {enterprise_name} with tags {agent_tag_names}...")
        with open(file_path, 'rb') as document_file:
            files = {"document": document_file}
            data = {
                "title": file_name,
                "storage_path": enterprise_data["id"],
                "tags": agent_tag_ids,
            }
            data = {k: v for k, v in data.items() if v is not None}
            try:
                response = self._request(method="POST", endpoint=self.upload_endpoint, files=files, data=data)
                logger.info(f"Successfully uploaded {file_name}.")
                return response
            except Exception as err:
                logger.error(f"An error occurred during uploading {file_name}: {err}")
                return None

    def download_document(self,
                          document_id: int,
                          save_path: Path | None = None,
                          original: bool = True) -> Tuple[bool, str]:
        """
        Download a document from the Paperless service.

        Arguments:
        document_id : int - ID of the document to download.
        save_path : Path | None - Path to save the downloaded document. If not provided, use the default download path.
        original : bool - Whether to download the original document (default is False).

        Returns:
        Tuple[bool, str]- The status of the download operation and file name.
        """
        download_endpoint = f"/api/documents/{document_id}/download/"
        if original:
            download_endpoint += "?original=true"

        document_name = self.get_document_name(document_id)
        if save_path is None:
            save_path = self._get_download_path(document_name)
        else:
            save_path = Path(save_path) / document_name

        headers = {'Authorization': f'Token {self.token}'}

        def download_and_save():
            response = requests.get(f"{self.base_url}{download_endpoint}", headers=headers, stream=True)
            response.raise_for_status()
            self._save_document(response, save_path)
            return True, str(save_path)

        if save_path.exists():
            return False, str(save_path)

        try:
            return download_and_save()
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 401:
                self.refresh_token()
                headers['Authorization'] = f'Token {self.token}'
                try:
                    return download_and_save()
                except Exception as retry_err:
                    logger.error(f"An error occurred during retry: {retry_err}")
                    return False, str(save_path)
            else:
                logger.error(f"HTTP error occurred: {http_err}")
                return False, str(save_path)
        except Exception as err:
            logger.error(f"An error occurred during request: {err}")
            return False, str(save_path)

    def _find_document_by_filename_and_enterprise(self,
                                                  filename: str,
                                                  enterprise_name: str) -> Dict[str, Any] | None:
        """
        Find a document by its filename and enterprise ID.

        Arguments:
        filename : str - The name of the file.
        enterprise_name : int - The name of the enterprise.

        Returns:
        Dict[str, Any] | None - The found document if any, otherwise None.
        """
        search_results = self.search_documents(filename=filename, enterprise_name=enterprise_name)
        for document in search_results.get("results", []):
            if document.get("original_file_name") == filename:
                return document
        logger.error(f"No document found with name {filename} in enterprise {enterprise_name}")
        return None

    def _get_agent_tag_ids(self, agent_tag_names: List[str]) -> List[int]:
        """
        Get the agent tag IDs for the given list of agent tag names.

        Arguments:
        agent_tag_names : List[str] - The list of agent tag names.

        Returns:
        List[int] - The list of agent tag IDs.
        """
        agent_tag_ids = []
        for agent_tag_name in agent_tag_names:
            agent_tag = self.get_or_create_agent_tag(agent_tag_name)
            if agent_tag:
                agent_tag_ids.append(agent_tag.get("id"))
        if not agent_tag_ids:
            logger.error(f"Failed to find or create new agent tags: {agent_tag_names}")
        return agent_tag_ids

    def _update_document_tags(self, document_id: int, tag_ids: List[int]) -> Dict[str, Any] | None:
        """
        Update the tags of a document with the given tag IDs.

        Arguments:
        document_id : int - The ID of the document.
        tag_ids : List[int] - The list of tag IDs.

        Returns:
        Dict[str, Any] | None - Updated document metadata if successful, otherwise None.
        """
        update_endpoint = f"{self.documents_endpoint}{document_id}/"
        update_data = {"tags": tag_ids}

        try:
            updated_document = self._request(method="PATCH", endpoint=update_endpoint, json=update_data)
            if updated_document:
                logger.info(f"Successfully updated tags for document ID {document_id}")
                return updated_document
            else:
                logger.error(f"Failed to update document ID {document_id}")
                return None
        except Exception as err:
            logger.error(f"An error occurred while updating document ID {document_id}: {err}")
            return None

    def update_agent_tags(self,
                          filename: str,
                          enterprise_name: str,
                          new_agent_tags: List[str]) -> Dict[str, Any] | None:
        """
        Update the tags for a specific file.

        Arguments:
        filename : str - The name of the file.
        enterprise_name : str - The name of the enterprise collection.
        new_agent_tags : List[str] - The new list of agent tags.

        Returns:
        Dict[str, Any] | None - Updated file metadata if successful, otherwise None.
        """
        document_to_update = self._find_document_by_filename_and_enterprise(filename, enterprise_name)
        if not document_to_update:
            return None

        new_agent_tag_ids = self._get_agent_tag_ids(new_agent_tags)
        if not new_agent_tag_ids:
            return None

        document_id = document_to_update.get("id")
        return self._update_document_tags(document_id, new_agent_tag_ids)

    def add_agent_tags(self,
                       filename: str,
                       enterprise_name: str,
                       additional_agent_tags: List[str]) -> Dict[str, Any] | None:
        """
        Add new tags to a specific file without duplicating existing tags.

        Arguments:
        filename : str - The name of the file.
        enterprise_name : str - The name of the enterprise collection.
        additional_agent_tags : List[str] - The list of new agent tags to add.

        Returns:
        Dict[str, Any] | None - Updated file metadata if successful, otherwise None.
        """
        document_to_update = self._find_document_by_filename_and_enterprise(filename, enterprise_name)
        if not document_to_update:
            return None

        existing_tag_ids = set(document_to_update.get("tags", []))
        new_agent_tag_ids = self._get_agent_tag_ids(additional_agent_tags)
        if not new_agent_tag_ids:
            return None

        combined_tag_ids = list(existing_tag_ids.union(set(new_agent_tag_ids)))

        document_id = document_to_update.get("id")
        return self._update_document_tags(document_id, combined_tag_ids)

    def delete_document(self, filename: str, enterprise_name: str) -> bool:
        """
        Completely delete a document by its filename and enterprise ID.

        Arguments:
        filename : str - The name of the file to delete.
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        bool - True if deletion was successful, False otherwise.
        """
        document_to_delete = self._find_document_by_filename_and_enterprise(filename, enterprise_name)
        if not document_to_delete:
            return False

        document_id = document_to_delete.get("id")
        delete_endpoint = f"{self.documents_endpoint}{document_id}/"
        trash_endpoint = "/api/trash/"

        try:
            # Step 1: Delete the document (move to trash)
            delete_response = requests.delete(f"{self.base_url}{delete_endpoint}",
                                              headers={'Authorization': f'Token {self.token}'})
            delete_response.raise_for_status()

            # Step 2: Permanently delete the document from trash
            trash_payload = {"action": "empty", "documents": [document_id]}
            permanent_delete_response = requests.post(f"{self.base_url}{trash_endpoint}",
                                                      headers={'Authorization': f'Token {self.token}'},
                                                      json=trash_payload)
            permanent_delete_response.raise_for_status()

            logger.info(f"Successfully permanently deleted document '{filename}' with ID {document_id}")
            return True

        except requests.exceptions.HTTPError as http_err:
            logger.error(
                f"HTTP error occurred during deletion of document '{filename}' with ID {document_id}: {http_err}"
            )
            return False
        except Exception as err:
            logger.error(f"An error occurred while deleting document '{filename}' with ID {document_id}: {err}")
            return False

    def get_document_and_metadata(self, filename: str, enterprise_name: str) -> Dict[str, Any] | None:
        """
        Get a document and its metadata from the Paperless service.

        Arguments:
        filename : str - The name of the file to retrieve.
        enterprise_name : str - The name of the enterprise.

        Returns:
        Dict[str, Any] | None - Dictionary containing document data and metadata if successful, otherwise None.
        """
        try:
            search_results = self.search_documents(filename=filename, enterprise_name=enterprise_name)
            document_to_download = None
            for document in search_results.get("results", []):
                if document.get("original_file_name") == filename:
                    document_to_download = document
                    break

            if not document_to_download:
                logger.error(f"No document found with name {filename} in enterprise {enterprise_name}")
                return None

            document_id = document_to_download.get("id")

            # Get the document metadata
            document_metadata = self._request("GET", f"/api/documents/{document_id}/")
            if not document_metadata:
                return None

            # Get the document data
            headers = {'Authorization': f'Token {self.token}'}
            download_endpoint = f"/api/documents/{document_id}/download/"
            response = requests.get(f"{self.base_url}{download_endpoint}", headers=headers)
            response.raise_for_status()

            document_data = io.BytesIO(response.content)

            return {
                "metadata": document_metadata,
                "file": document_data,
                "filename": document_metadata["original_file_name"]
            }
        except Exception as err:
            logger.error(
                f"An error occurred while getting document {filename} from enterprise {enterprise_name}: {err}")
            return None
