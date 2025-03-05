import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, List

from shared_libraries.core.logger.create_logger import logger
from shared_libraries.docstore.clients.interface import StorageClient
from shared_libraries.docstore.clients.paperless import PaperlessClient
from shared_libraries.docstore.schemas import Enterprise, FileMetadata, AgentTag, DownloadStatus


class DocumentStore:
    def __init__(self, client: StorageClient | None = None):
        """
        Initialize the DocumentStore.

        Arguments:
        client : StorageClient | None - The storage client to use. Defaults to PaperlessClient.
        """
        self.client = client
        if self.client is None:
            self.client = PaperlessClient()

    def create_enterprise_collection(self, enterprise_name: str) -> Enterprise | None:
        """
        Create a new enterprise collection.

        Arguments:
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        Enterprise | None - The created enterprise data collection, or None if an error occurred.
        """
        try:
            result = self.client.create_enterprise_collection(enterprise_name)
            if result:
                return Enterprise(object_id=result["id"],
                                  name=result["name"])
        except Exception as e:
            logger.error(e)
        return None

    def get_enterprise_collection(self, enterprise_name: str) -> Enterprise | None:
        """
        Get the enterprise data collection by enterprise_name.

        Arguments:
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        Enterprise | None - The enterprise data collection if found, otherwise None.
        """
        try:
            result = self.client.get_enterprise_collection(enterprise_name)
            if result:
                return Enterprise(object_id=result["id"],
                                  name=result["name"])
        except Exception as e:
            logger.error(e)
        return None

    def get_enterprise_collection_by_id(self, enterprise_id: int) -> Enterprise | None:
        """
        Get an enterprise collection data by its ID.

        Arguments:
        enterprise_id : int - The ID of the enterprise collection.

        Returns:
        Enterprise | None - The enterprise collection data if found, otherwise None.
        """
        try:
            result = self.client.get_enterprise_collection_by_id(enterprise_id)
            if result:
                return Enterprise(object_id=result["id"],
                                  name=result["name"])
        except Exception as e:
            logger.error(e)
        return None

    def get_or_create_enterprise_collection(self, enterprise_name: str) -> Enterprise | None:
        """
        Get or create an enterprise collections.

        Arguments:
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        Enterprise | None - The created or existing enterprise data collection, or None if an error occurred.
        """
        try:
            result = self.client.get_or_create_enterprise_collection(enterprise_name)
            if result:
                return Enterprise(object_id=result["id"],
                                  name=result["name"])
        except Exception as e:
            logger.error(e)
        return None

    def list_enterprise_collections(self) -> List[Enterprise]:
        """
        Get all enterprise collections.

        Returns:
        List[Enterprise] - The list of enterprise collections.
        """
        enterprises = []
        try:
            results = self.client.list_enterprise_collections()
            for result in results:
                enterprises.append(
                    Enterprise(object_id=result["id"],
                               name=result["name"])
                )
        except Exception as e:
            logger.error(e)
        return enterprises

    def create_agent_tag(self, name: str) -> AgentTag | None:
        """
        Create a new agent tag.

        Arguments:
        name : str - The name of the agent tag.

        Returns:
        AgentTag | None - The created agent tag data, or None if an error occurred.
        """
        try:
            result = self.client.create_agent_tag(name)
            if result:
                return AgentTag(object_id=result["id"],
                                slug=result["slug"],
                                name=result["name"],
                                document_count=result["document_count"],
                                owner=result["owner"],
                                user_can_change=result["user_can_change"])
        except Exception as e:
            logger.error(e)
        return None

    def get_agent_tag(self, name: str) -> AgentTag | None:
        """
        Get an agent tag by its name.

        Arguments:
        name : str - The name of the agent tag.

        Returns:
        AgentTag | None - The agent tag data if found, otherwise None.
        """
        try:
            result = self.client.get_agent_tag(name)
            if result:
                return AgentTag(object_id=result["id"],
                                slug=result["slug"],
                                name=result["name"],
                                document_count=result["document_count"],
                                owner=result["owner"],
                                user_can_change=result["user_can_change"])
        except Exception as e:
            logger.error(e)
        return None

    def get_agent_tag_by_id(self, agent_tag_id: int) -> AgentTag | None:
        """
        Get an agent tag data by its ID.

        Arguments:
        agent_tag_id : int - The ID of the agent tag.

        Returns:
        AgentTag | None - The agent tag data if found, otherwise None.
        """
        try:
            result = self.client.get_agent_tag_by_id(agent_tag_id)
            if result:
                return AgentTag(object_id=result["id"],
                                slug=result["slug"],
                                name=result["name"],
                                document_count=result["document_count"],
                                owner=result["owner"],
                                user_can_change=result["user_can_change"])
        except Exception as e:
            logger.error(e)
        return None

    def get_or_create_agent_tag(self, name: str) -> AgentTag | None:
        """
        Get or create an agent tag.

        Arguments:
        name : str - The name of the agent tag.

        Returns:
        AgentTag | None - The created or existing agent tag data, or None if an error occurred.
        """
        try:
            result = self.client.get_or_create_agent_tag(name)
            if result:
                return AgentTag(object_id=result["id"],
                                slug=result["slug"],
                                name=result["name"],
                                document_count=result.get("document_count", 0),
                                owner=result["owner"],
                                user_can_change=result["user_can_change"])
        except Exception as e:
            logger.error(e)
        return None

    def list_agent_tags(self) -> List[AgentTag]:
        """
        Get all agent tags.

        Returns:
        List[AgentTag] - The list of agent tags.
        """
        agent_tags = []
        try:
            results = self.client.list_agent_tags()
            for result in results:
                agent_tags.append(
                    AgentTag(object_id=result["id"],
                             slug=result["slug"],
                             name=result["name"],
                             document_count=result["document_count"],
                             owner=result["owner"],
                             user_can_change=result["user_can_change"])
                )
        except Exception as e:
            logger.error(e)
        return agent_tags

    def get_task_status(self, task_id: str) -> Dict[str, Any] | None:
        """
        Get the status of a task by its UUID.

        Arguments:
        task_id : str - UUID of the task.

        Returns:
        Dict[str, Any] | None - The task status data if found, otherwise None.
        """
        try:
            result = self.client.get_task_status(task_id)
            if result:
                return result
        except Exception as e:
            logger.error(e)
        return None

    def search_documents(self,
                         filename: str = "",
                         enterprise_name: str = "",
                         agent_names: List[str] | None = None) -> List[FileMetadata]:
        """
        Search for documents based on various filters.

        Arguments:
        filename : str - The filename to search for.
        enterprise_name : str - The name of the enterprise.
        agent_names : List[str] | None - The list of agent names.

        Returns:
        List[FileMetadata] - The search results from the API.
        """
        metadatas = []
        try:
            results = self.client.search_documents(
                filename=filename,
                enterprise_name=enterprise_name,
                agent_names=agent_names
            )
            if results:
                enterprise_list = self.client.list_enterprise_collections()
                enterprise_dict = {item["id"]: item["name"] for item in enterprise_list}
                agent_tag_list = self.client.list_agent_tags()
                agent_tag_dict = {item["id"]: item["name"] for item in agent_tag_list}
                metadatas = [FileMetadata(**result) for result in results["results"]]
                for metadata in metadatas:
                    for agent_tag_id in metadata.agent_tag_ids:
                        agent_tag_name = agent_tag_dict.get(agent_tag_id, "")
                        if agent_tag_name:
                            metadata.agent_tag_names.append(agent_tag_name)
                        else:
                            logger.warning(f"Agent tag ID {agent_tag_id} wasn't found in document storage.")
                    enterprise_name = enterprise_dict.get(metadata.enterprise_object_id, "")
                    metadata.enterprise_name = enterprise_name
                    if not enterprise_name:
                        logger.warning(
                            f"Enterprise ID {metadata.enterprise_object_id} wasn't found in document storage."
                        )
        except Exception as e:
            logger.error(e)
        return metadatas

    def upload_document(self, file_path: str,
                        enterprise_name: str,
                        agent_tag_names: List[str] | None = None) -> str | None:
        """
        Upload a document to the service.

        Arguments:
        file_path : str - Path to the document file to upload.
        enterprise_name : str - The name of the enterprise.
        agent_tag_names : List[str] | None - List of agent tags names.

        Returns:
        str | None - Task ID, or None if an error occurred.
        """
        try:
            return self.client.upload_document(file_path=file_path,
                                               enterprise_name=enterprise_name,
                                               agent_tag_names=agent_tag_names)
        except Exception as e:
            logger.error(e)
        return None

    def upload_enterprise_list(self, enterprise_name: str, enterprise_list: list[str],
                               agent_names: list[str] | None = None):
        """
        Upload an enterprise list to the service.

        Arguments:
        enterprise_name : str - The name of the enterprise.
        enterprise_list : list[str] - The list of enterprise data to upload.
        agent_names : list[str] | None - List of agent names.

        Returns:
        str | None - Task ID, or None if an error occurred.
        """
        unique_file_name = f"graph_file__{enterprise_name}__{uuid.uuid4()}.txt"
        response = None

        with tempfile.NamedTemporaryFile(delete=False, prefix=unique_file_name, mode='w', suffix='.txt') as temp_file:
            temp_file_path = temp_file.name
            try:
                for line in enterprise_list:
                    temp_file.write(line + "\n")
                logger.info(f"Data written to temporary file {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to write to temporary file: {e}")
                return None

        try:
            response = self.client.upload_document(temp_file_path, enterprise_name, agent_names)
            logger.info(f"Response from service: {response}")
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
        finally:
            try:
                os.remove(temp_file_path)
                logger.info(f"Temporary file {temp_file_path} has been deleted.")
            except Exception as e:
                logger.warning(f"Unable to delete temporary file {temp_file_path}: {e}")
        return response

    def download_document_by_id(self,
                                document_id: int,
                                save_path: Path | None = None,
                                original: bool = False) -> DownloadStatus:
        """
        Download a document from service.

        Arguments:
        document_id : int - ID of the document to download.
        save_path : str - Path to save the downloaded document as.
        original : bool - Whether to download the original document (default is False).

        Returns:
        DownloadStatus - Status of the download.
        """
        try:
            result, document_name = self.client.download_document(
                document_id=document_id,
                save_path=save_path,
                original=original
            )
            if result:
                return DownloadStatus(status=True, message=f"File {document_name} downloaded")
            else:
                return DownloadStatus(status=False, message=f"File {document_name} already exists")
        except Exception as e:
            logger.error(e)
            return DownloadStatus(status=False, message=f"Error. File with id {document_id} not downloaded")

    def download_document(self,
                          filename: str,
                          enterprise_name: str,
                          save_path: Path | None = None,
                          original: bool = True) -> DownloadStatus:
        """
        Download a document from service by filename and enterprise name.

        Arguments:
        filename : str - The name of the file to download.
        enterprise_name : str - The name of the enterprise collection.
        save_path : Path | None - Path to save the downloaded document.
        original : bool - Whether to download the original document (default is False).

        Returns:
        DownloadStatus - Status of the download.
        """
        try:
            search_results = self.client.search_documents(filename=filename, enterprise_name=enterprise_name)
            document_to_download = None
            for document in search_results.get("results", []):
                if document.get("original_file_name") == filename:
                    document_to_download = document
                    break

            if not document_to_download:
                return DownloadStatus(
                    status=False,
                    message=f"No document found with name {filename} in enterprise {enterprise_name}"
                )

            document_id = document_to_download.get("id")
            result, document_name = self.client.download_document(
                document_id=document_id,
                save_path=save_path,
                original=original
            )
            if result:
                return DownloadStatus(status=True, message=f"File {document_name} downloaded")
            else:
                return DownloadStatus(status=False, message=f"File {document_name} already exists")

        except Exception as e:
            logger.error(e)
            return DownloadStatus(
                status=False,
                message=f"Error. File with name {filename} and enterprise {enterprise_name} not downloaded")

    def update_agent_tags(self,
                          filename: str,
                          enterprise_name: str,
                          new_agent_tags: List[str]) -> Dict[str, Any] | None:
        """
        Update the tags for a specific file.

        Arguments:
        filename : str - The name of the file.
        enterprise_str : str - The name of the enterprise collection.
        new_agent_tags : List[str] - The new list of agent tags.

        Returns:
        Dict[str, Any] | None - Updated file metadata if successful, otherwise None.
        """
        try:
            return self.client.update_agent_tags(filename, enterprise_name, new_agent_tags)
        except Exception as e:
            logger.error(e)
        return None

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
        try:
            return self.client.add_agent_tags(filename, enterprise_name, additional_agent_tags)
        except Exception as e:
            logger.error(e)
        return None

    def delete_document(self, filename: str, enterprise_name: str) -> bool:
        """
        Completely delete a document by its filename and enterprise name.

        Arguments:
        filename : str - The name of the file to delete.
        enterprise_name : int - The name of the enterprise collection.

        Returns:
        bool - True if deletion was successful, False otherwise.
        """
        try:
            return self.client.delete_document(filename, enterprise_name)
        except Exception as e:
            logger.error(e)
        return False

    def get_document_data(self, filename: str, enterprise_name: str) -> Dict[str, Any] | None:
        """
        Get document data and metadata by filename and enterprise ID.

        Arguments:
        filename : str - The name of the file to retrieve.
        enterprise_name : str - The name of the enterprise collection.

        Returns:
        Dict[str, Any] | None - Dictionary containing document data and metadata if successful, otherwise None.
        """
        try:
            return self.client.get_document_and_metadata(filename, enterprise_name)
        except Exception as e:
            logger.error(e)
        return None


if __name__ == "__main__":

    document_store = DocumentStore()
    enterprise_name = "Enterprise"
    filename = "Diagram1.png"
    path = "C:\\Work\\"
    agent_names = ["Agent1", "Agent2", "Agent3"]
    save_path = "C:\\Work\\Docs"
    file_path = path + filename

    # Enterprise methods
    enterprise = document_store.get_or_create_enterprise_collection(enterprise_name=enterprise_name)
    if enterprise:
        enterprise = enterprise.model_dump()
    print("Enterprise:", enterprise)

    enterprise = document_store.get_enterprise_collection(enterprise_name=enterprise_name)
    if enterprise:
        enterprise = enterprise.model_dump()
    print("Enterprise:", enterprise)

    enterprise = document_store.list_enterprise_collections()
    print("Enterprises:", enterprise)

    # Agent tags methods
    for agent_name in agent_names:
        agent_tag = document_store.get_or_create_agent_tag(name=agent_name)
        print("Agent_tag:", agent_tag)

    agent_tag = document_store.get_agent_tag(name=agent_names[0])
    print("Agent_tag:", agent_tag)

    agent_tags = document_store.list_agent_tags()
    print("Agent_tags:", agent_tags)

    # Uploading a document
    task_id = document_store.upload_document(file_path, enterprise_name, agent_names)
    print(f"Upload Task ID: {task_id}")

    # Upload enterprise list
    enterprise_graph = [
        {
            "9f1a327ce0204b08a3683fb75067f76e": "Business service - Customer Support Service:\n"
                                                "Customer Support Service Attributes:\n"
                                                "* actor: Customers, Support Representativ...elationships:\n"
                                                "* USES => (Business service - CRM)\n"
                                                "* USES => (Business service - VOIP)\n"
                                                "* USES => (Business service - Zendesk)"
        },
        {
            "e14c4154ad434538ab3249975f5b24b2": "Application - Zendesk:\n"
                                                "Zendesk Attributes:\n"
                                                "* actor: Customers, Support Representatives\n"
                                                "* name: Zendesk\n"
                                                "* description: A s... "
                                                "https://emakinatr.atlassian.net/wiki/spaces/EPMESL/pages/4179689473/Zendesk_2\n"
                                                "* technology_stack: ['Zendesk', 'VOIP', 'CRM']"
        },
        {
            "2e2750881207438dbcc25a65ad822c2d": "Application - VOIP:\n"
                                                "VOIP Attributes:\n"
                                                "* actor: Customers, Support Representatives\n"
                                                "* name: VOIP\n"
                                                "* description: A service fa...rl: "
                                                "https://emakinatr.atlassian.net/wiki/spaces/EPMESL/pages/4123492456/VOIP_2\n"
                                                "* technology_stack: ['Zendesk', 'VOIP', 'CRM']"
        }
    ]
    enterprise_list = [node_repr for node_dict in enterprise_graph for node_repr in node_dict.values()]

    document_store.upload_enterprise_list(enterprise_name=enterprise_name, enterprise_list=enterprise_list)

    # Search documents using filter
    metadata = document_store.search_documents()
    # metadata = document_store.search_documents(filename=filename)
    for num, data in enumerate(metadata, 1):
        print(f"{num}. Metadata: {data}")

    # Check task
    task_info = document_store.get_task_status(task_id)
    print("Task info:", task_info)

    # Downloading a document by ID
    # document_id = 14  # Replace with actual document ID
    # download_status = document_store.download_document_by_id(
    #     document_id=document_id,
    #     save_path=Path(save_path),
    #     original=True
    # )
    # print("Download Status:", download_status)

    # Downloading a document by filename and enterprise ID
    download_status = document_store.download_document(filename=filename,
                                                       enterprise_name=enterprise_name,
                                                       save_path=Path(save_path))
    print("Download status:", download_status)

    # Updating agent tags of a document
    update_status = document_store.update_agent_tags(
        filename=filename,
        enterprise_name=enterprise_name,
        new_agent_tags=["new_tag_1", "new_tag_2"])
    if update_status:
        print(f"Updated file metadata: {update_status}")
    else:
        print("Failed to update file metadata")

    # Adding agent tags to a document
    add_tags_status = document_store.add_agent_tags(
        filename=filename,
        enterprise_name=enterprise_name,
        additional_agent_tags=["new_tag_2", "new_tag_3"])
    if add_tags_status:
        print(f"Updated file metadata: {add_tags_status}")
    else:
        print("Failed to add tags to the file")

    # Deleting a document
    delete_status = document_store.delete_document(filename, enterprise_name)
    if delete_status:
        print("Successfully deleted the document")
    else:
        print("Failed to delete the document")
