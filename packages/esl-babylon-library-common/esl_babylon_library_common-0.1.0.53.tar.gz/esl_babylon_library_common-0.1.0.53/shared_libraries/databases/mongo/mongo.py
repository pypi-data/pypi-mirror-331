import base64
import re
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import requests
from bson import ObjectId
from gridfs import GridFS
from pydantic import AnyUrl
from pymongo import ReturnDocument

from shared_libraries.core.config import app_common_config
from shared_libraries.core.logger.create_logger import logger
from shared_libraries.databases.mongo.get_mongo_client import get_mongo_client
from shared_libraries.utils.is_confluence_url import is_confluence_url


class MongoDBService:
    """A MongoDB class."""

    def __init__(self,
                 db_name: str = app_common_config.mongo_files_db_name) -> None:
        """
        Constructor method to initialize MongoDB client connection.
        """
        self.client = get_mongo_client()
        self.db = self.client.get_database(name=db_name)
        self.cache_db = self.client[app_common_config.mongo_cache_db_name]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Method to close MongoDB client connection."""
        self.client.close()

    @staticmethod
    def get_file_hash(file_data: bytes) -> str:
        """Method to get hash of a file.

        Arguments:
        file_data : bytes - The file data.

        Returns:
        str - The file hash.
        """
        file_hash = sha256(string=file_data).hexdigest()
        return file_hash

    def get_object_id(self,
                      query: dict[str, Any],
                      collection_name: str) -> ObjectId | None:
        """Gets object ids from collection using query.

        Arguments:
        query : dict[str, Any] - The query.
        collection_name : str - collection name.

        Returns:
        ObjectId | None - ObjectId if file exists, None otherwise.
        """
        # Check in small files
        file = self.db["small_" + collection_name].find_one(query)
        if file:
            return file.get("_id")

        # Check in large files
        fs = GridFS(database=self.db, collection="big_" + collection_name)
        file = fs.find_one(query)
        if file:
            return file._id

    def get_object_id_by_hash(self,
                              enterprise_id: int,
                              file_hash: str, collection_name: str) -> ObjectId | None:
        """Gets object id by file hash for an enterprise_id.

        Arguments:
        enterprise_id : int - The enterprise id.
        file_hash : str - The hash of file.

        Returns:
        ObjectId | None - ObjectId if file exists, None otherwise.
        """
        query = {"enterprise_id": enterprise_id, "file_hash": file_hash}

        return self.get_object_id(query=query, collection_name=collection_name)

    def get_object_id_by_url(self,
                             enterprise_id: int,
                             url: str,
                             collection_name: str = app_common_config.mongo_files_collection_name) -> ObjectId | None:
        """Gets object id by url for an enterprise_id.

        Arguments:
        enterprise_id : int - The enterprise id.
        url : str - The URL.

        Returns:
        ObjectId | None - ObjectId if url exists, None otherwise.
        """
        query = {"enterprise_id": enterprise_id, "url": url}

        return self.get_object_id(query=query, collection_name=collection_name)

    def insert_data(self,
                    file_data: bytes,
                    filename: str,
                    enterprise_id: int,
                    username: str,
                    collection_name: str,
                    additional_metadata: dict = None) -> tuple[ObjectId | None, bool | None]:
        """Method to insert file data.

        Arguments:
        file_data : bytes - The file data.
        file_name : str - The name of the file.
        enterprise_id : int - The enterprise id.
        username : str - The username.
        collection_name : str - collection name.
        additional_metadata : dict - Additional metadata for object.

        Returns:
        ObjectId - ObjectId if file properly inserted or exists, None otherwise.
        """
        file_hash = self.get_file_hash(file_data=file_data)
        try:
            object_id = self.get_object_id(query={"enterprise_id": enterprise_id, "file_hash": file_hash},
                                           collection_name=collection_name)
            if object_id:
                return object_id, False

            path_object = Path(filename)

            metadata = {
                "enterprise_id": enterprise_id,
                "user_name": username,
                "file_hash": file_hash,
                "file_name": filename,
                "file_ext": path_object.suffix,
                "current_date": datetime.utcnow(),
            }
            if additional_metadata:
                metadata.update(additional_metadata)
            if len(file_data) > 16 * 1024 * 1024:
                object_id = self.insert_big_file_data(file_data, metadata, collection_name)
            else:
                object_id = self.insert_small_file_data(file_data, metadata, collection_name)
            return object_id, True
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None, None

    def insert_big_file_data(self,
                             file_data: bytes,
                             metadata: dict[str, Any], collection_name: str) -> None | ObjectId:
        """Method to insert large file into GridFS using file_data.

        Arguments:
        file_data : bytes - The file data.
        metadata : dict[str, Any] - The metadata.

        Returns:
        ObjectId - The ObjectId of the inserted file or None in case of error.
        """
        try:
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            file_id = fs.put(file_data, **metadata)
            return file_id
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None

    def insert_small_file_data(self,
                               file_data: bytes,
                               metadata: dict[str, Any], collection_name: str) -> None | ObjectId:
        """Method to insert small file with Base64 encoding using file_data.

        Arguments:
        file_data : bytes - The file data.
        metadata : dict[str, Any] - The metadata.

        Returns:
        ObjectId - The ObjectId of the inserted file or None in case of error.
        """
        try:
            base64_data = base64.b64encode(file_data).decode("utf-8")
            metadata.update({"file_data": base64_data})
            inserted = self.db["small_" + collection_name].insert_one(metadata)
            return inserted.inserted_id
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None

    def insert_file(self,
                    file_path: Path,
                    enterprise_id: int,
                    username: str) -> tuple[ObjectId | None, bool | None]:
        """Method to insert file.

        Arguments:
        file_data : bytes - The file data.
        enterprise_id : int - The enterprise id.
        username : str - The username.


        Returns:
        ObjectId - ObjectId if file properly inserted or exists, and None in case of error.
        """
        with open(file_path, 'rb') as file:
            file_data = file.read()

        return self.insert_file_data(file_data=file_data,
                                     filename=file_path.name,
                                     enterprise_id=enterprise_id,
                                     username=username)

    def insert_graph_file(self,
                          file_path: Path,
                          enterprise_id: int,
                          collection_name: str = app_common_config.mongo_graph_files_collection_name
                          ) -> tuple[ObjectId | None, bool | None]:
        """Method to insert file from graph.

        Arguments:
        file_data : bytes - The file data.
        enterprise_id : int - The enterprise id.
        collection_name: str - Graph collection names (graph_files or graph_nodes).

        Returns:
        ObjectId - ObjectId if file properly inserted or exists, and None in case of error.
        """
        with open(file_path, 'rb') as file:
            file_data = file.read()

        return self.insert_file_data(file_data=file_data,
                                     filename=file_path.name,
                                     enterprise_id=enterprise_id,
                                     username="",
                                     collection_name=collection_name)

    def insert_file_data(self,
                         file_data: bytes,
                         filename: str,
                         enterprise_id: int,
                         username: str,
                         collection_name: str = app_common_config.mongo_files_collection_name,
                         ) -> tuple[ObjectId | None, bool | None]:
        """Method to insert file data.

        Arguments:
        file_data : bytes - The file data.
        file_name : str - The file name.
        enterprise_id : int - The enterprise id.
        username : str - The username.
        collection_name : str - collection name.
        additional_metadata : dict - Additional metadata for object.

        Returns:
        ObjectId - ObjectId if file properly inserted or exists, and None in case of error.
        """
        path_object = Path(filename)
        additional_metadata = {
            "downloaded": True,
            "url": None,
            "processing_status": 0 if path_object.suffix not in [".jpg", ".jpeg", ".png"] else None,
            "processing_status_hi_res": 0 if path_object.suffix not in [".txt", ".json"] else None,
            "extract_statistics": {},
            "extract_statistics_hi_res": {},
            "enrich_statistics": {},
            "enrich_statistics_hi_res": {}
        }
        return self.insert_data(
            file_data,
            filename,
            enterprise_id,
            username,
            collection_name,
            additional_metadata
        )

    def insert_url(self,
                   url: AnyUrl,
                   enterprise_id: int,
                   username: str,
                   collection_name: str = app_common_config.mongo_files_collection_name) -> ObjectId | None:
        try:
            object_id = self.get_object_id_by_url(enterprise_id=enterprise_id,
                                                  url=url.unicode_string())
            if object_id:
                return object_id

            metadata = {
                "enterprise_id": enterprise_id,
                "user_name": username,
                "file_hash": None,
                "file_name": None,
                "file_ext": None,
                "current_date": datetime.utcnow(),
                "downloaded": False,
                "url": url.unicode_string(),
                "processing_status": 0,
                "processing_status_hi_res": 0,
                "extract_statistics": {},
                "extract_statistics_hi_res": {},
                "enrich_statistics": {},
                "enrich_statistics_hi_res": {}
            }
            object_id = self.db[collection_name].insert_one(metadata)
            return object_id.inserted_id
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None

    def insert_confluence_page(self,
                               confluence_client,
                               object_id: str | ObjectId,
                               page_url: str,
                               enterprise_id: int,
                               user_name: str) -> None | ObjectId:

        page_id, page_content = confluence_client.get_confluence_page_content(page_url=page_url)

        if not page_id or not page_content:
            return None

        object_id, updated = self.update_file_data(
            object_id=object_id,
            file_data=page_content["html"].encode(),
            filename=page_id + ".html",
            enterprise_id=enterprise_id,
            username=user_name,
            collection_name=app_common_config.mongo_files_collection_name,
            additional_metadata={
                "images": page_content["images_base64"],
                "html_type": "confluence",
                "url": page_url
            }
        )
        return object_id

    def insert_html_page(self,
                         object_id: str | ObjectId,
                         page_url: str,
                         enterprise_id: int,
                         user_name: str) -> None | ObjectId:

        page_content = {
            "html": "",
            "images_base64": []
        }
        try:
            response = requests.get(page_url)
            page_content["html"] = response.text
            img_regex = re.compile(r'<img[^>]+src="([^">]+)"')

            for match in img_regex.finditer(page_content["html"]):
                img_url = match.group(1)
                try:
                    response = requests.get(img_url)
                    response.raise_for_status()
                except requests.exceptions.MissingSchema as e:
                    message = (f"Something went wrong: {e}. "
                               f"Invalid image URL: '{img_url}'. Skipping image.")
                    logger.warning(msg=message,
                                   exc_info=True)
                    continue

                page_content["images_base64"].append(response.content)
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None

        object_id, updated = self.update_file_data(
            object_id=object_id,
            file_data=page_content["html"].encode(),
            filename=page_url + ".html",
            enterprise_id=enterprise_id,
            username=user_name,
            collection_name=app_common_config.mongo_files_collection_name,
            additional_metadata={
                "images": page_content["images_base64"],
                "html_type": "webpage",
                "url": page_url
            }
        )
        return object_id

    def insert_agent_file_data(self,
                               file_data: bytes,
                               filename: str,
                               enterprise_id: int,
                               username: str,
                               collection_name: str = app_common_config.mongo_agent_files_collection_name,
                               ) -> tuple[ObjectId | None, bool | None]:
        """Method to insert agent file data.

        Arguments:
        file_data : bytes - The file data.
        file_name : str - The file name.
        enterprise_id : int - The enterprise id.
        username : str - The username.
        collection_name : str - collection name.

        Returns:
        ObjectId - ObjectId if file properly inserted or exists, and None in case of error.
        """
        path_object = Path(filename)
        additional_metadata = {
            "downloaded": True,
            "url": None,
            "processing_status": 0 if path_object.suffix not in [".jpg", ".jpeg", ".png"] else None,
            "processing_status_hi_res": 0 if path_object.suffix not in [".txt", ".json"] else None,
        }
        return self.insert_data(
            file_data,
            filename,
            enterprise_id,
            username,
            collection_name,
            additional_metadata
        )

    def update_file_data(self,
                         object_id: ObjectId | str,
                         file_data: bytes,
                         filename: str,
                         enterprise_id: int,
                         username: str,
                         collection_name: str,
                         additional_metadata: dict = None) -> tuple[ObjectId | None, bool | None]:
        try:
            file_hash = self.get_file_hash(file_data=file_data)

            files = self.get_files(query={'_id': ObjectId(oid=object_id)},
                                   collection_name=collection_name)
            if not files:
                raise FileNotFoundError(f"File with oid {object_id} is not found in collection '{collection_name}'")

            if files[0].get("file_data") == file_data:
                logger.info(f"File data has not changed")
                return object_id, False

            path_object = Path(filename)
            metadata = {
                "enterprise_id": enterprise_id,
                "user_name": username,
                "file_hash": file_hash,
                "file_name": filename,
                "file_ext": path_object.suffix,
                "current_date": datetime.utcnow(),
                "downloaded": True,
                "url": None,
                "processing_status": 0 if path_object.suffix not in [".jpg", ".jpeg", ".png"] else None,
                "processing_status_hi_res": 0 if path_object.suffix not in [".txt", ".json"] else None,
                "extract_statistics": {},
                "extract_statistics_hi_res": {},
                "enrich_statistics": {},
                "enrich_statistics_hi_res": {}
            }

            if additional_metadata:
                metadata.update(additional_metadata)

            if len(file_data) > 16 * 1024 * 1024:
                object_id = self.update_big_file_data(object_id, file_data, metadata, collection_name)
            else:
                object_id = self.update_small_file_data(object_id, file_data, metadata, collection_name)

            return object_id, True
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None, None

    def update_big_file_data(self,
                             object_id: ObjectId | str,
                             file_data: bytes,
                             metadata: dict[str, Any],
                             collection_name: str) -> ObjectId | None:
        try:
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            fs.delete(ObjectId(oid=object_id))  # Remove the old file
            new_file_id = fs.put(file_data, **metadata)  # Insert the new file data
            return new_file_id
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None

    def update_small_file_data(self,
                               object_id: ObjectId,
                               file_data: bytes,
                               metadata: dict[str, Any],
                               collection_name: str) -> ObjectId | None:
        try:
            collection_name = f"small_{collection_name}"
            base64_data = base64.b64encode(file_data).decode("utf-8")
            metadata.update({"file_data": base64_data})
            result = self.db[collection_name].find_one_and_update(filter={'_id': ObjectId(oid=object_id)},
                                                                  update={"$set": metadata},
                                                                  upsert=True,
                                                                  return_document=ReturnDocument.AFTER)
            if result:
                return result['_id']
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
        return None

    def download_inserted_page(self,
                               confluence_client,
                               enterprise_id: int,
                               username: str,
                               url_id: str) -> str:
        url = self.get_url_by_id(enterprise_id=enterprise_id,
                                 url_id=url_id)
        if not url:
            raise ValueError(f'url is empty value')

        if is_confluence_url(url=url):
            object_id = self.insert_confluence_page(
                confluence_client=confluence_client,
                object_id=url_id,
                page_url=url,
                enterprise_id=enterprise_id,
                user_name=username)
        else:
            object_id = self.insert_html_page(
                object_id=url_id,
                page_url=url,
                enterprise_id=enterprise_id,
                user_name=username,
            )
        return url_id

    def get_url_by_id(self,
                      enterprise_id: int,
                      url_id: str, collection_name: str = app_common_config.mongo_files_collection_name) -> str | None:
        query = {"enterprise_id": enterprise_id,
                 "_id": ObjectId(url_id)}

        file = self.db["small_" + collection_name].find_one(query)
        if file:
            return file.get("url")

        # Check in large files
        fs = GridFS(database=self.db, collection="big_" + collection_name)
        file = fs.find_one(query)
        if file:
            return file.url

        return None

    def delete_files(self,
                     query: dict[str, Any],
                     collection_name: str = app_common_config.mongo_files_collection_name) -> str | None:
        """Method to delete files based on the query.

        Arguments:
        query : dict[str, Any] - The query.
        """
        try:
            if "_id" in query:
                query["_id"] = ObjectId(query["_id"])
            # Delete small files
            self.db["small_" + collection_name].delete_many(query)

            # Delete big files
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            big_files = fs.find(query)
            for file in big_files:
                fs.delete(file._id)
            return query["_id"]
        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
            return None

    def get_files(self,
                  query: dict[str, Any], collection_name: str = app_common_config.mongo_files_collection_name) -> list[
        dict[str, Any]]:
        """Gets all files with metadata based on the query.

        Arguments:
        query : dict[str, Any] - The query.

        Returns:
        list[dict[str, Any]] - A list of dictionaries that contains the metadata and file data.
        """
        results = []
        try:
            # Find small files
            small_files = self.db["small_" + collection_name].find(query)
            for file in small_files:
                data = file.pop("file_data", None)
                file_data = base64.b64decode(data) if data else None
                metadata = {"file_data": file_data}
                metadata.update(file)
                results.append(metadata)

            # Find big files
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            big_files = fs.find(query)
            for file in big_files:
                file_data = file.read()
                metadata = file.__dict__["_file"]
                metadata.update({"file_data": file_data})
                results.append(metadata)

            for result in results:
                result["_id"] = str(result["_id"])

        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)

        return results

    def get_files_metadata(self,
                           query: dict[str, Any],
                           collection_name: str = app_common_config.mongo_files_collection_name) -> \
            list[dict[str, Any]]:
        """Gets metadata for all files based on the query.

        Arguments:
        query : dict[str, Any] - The query.

        Returns:
        list[dict[str, Any]] - A list of dictionaries that contains the metadata and file data.
        """
        results = []
        try:
            # Find small files
            small_files = self.db["small_" + collection_name].find(query)
            for file in small_files:
                file.pop("file_data", None)
                results.append(file)

            # Find big files
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            big_files = fs.find(query)
            for file in big_files:
                metadata = file.__dict__["_file"]
                results.append(metadata)

            for result in results:
                result["_id"] = str(result["_id"])

        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)

        return results

    def delete_records(self, query: dict, collection_name: str):
        result = self.db[collection_name].delete_many(query)
        return result.deleted_count

    def update_enrich_statistics(self, file_names, enterprise_id, processing_status, strategy,
                                 ask_statistics_field_name,
                                 nodes_count,
                                 nodes_processed):
        """Update the 'statistics' field of a document in MongoDB."""
        collection_name = app_common_config.mongo_files_collection_name
        status_field = "processing_status" if strategy == "fast" else f"processing_status_{strategy}"
        try:
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            query = {"file_name": {"$in": file_names}, "enterprise_id": enterprise_id, status_field: processing_status}
            file = fs.find_one(query)
            if file:
                self.db["big_" + collection_name].files.update_many(
                    query,
                    {
                        "$inc": {
                            f"{ask_statistics_field_name}.nodes_count": nodes_count,
                            f"{ask_statistics_field_name}.nodes_processed": nodes_processed
                        }
                    }
                )
                return

            self.db["small_" + collection_name].update_many(
                query,
                {
                    "$inc": {
                        f"{ask_statistics_field_name}.nodes_count": nodes_count,
                        f"{ask_statistics_field_name}.nodes_processed": nodes_processed
                    }
                }
            )

        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)

    def update_statistics(self, file_name, enterprise_id, processing_status, strategy, ask_statistics_field_name,
                          chunk_count,
                          chunk_size, rep):
        """Update the 'statistics' field of a document in MongoDB."""
        collection_name = app_common_config.mongo_files_collection_name
        status_field = "processing_status" if strategy == "fast" else f"processing_status_{strategy}"
        try:
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            query = {"file_name": file_name, "enterprise_id": enterprise_id, status_field: processing_status}
            file = fs.find_one(query)
            if file:
                # ask_stats = file.get(ask_statistics_field_name, {})
                # chunk_count = ask_stats.get('chunk_count', 0)
                # chunk_processed = ask_stats.get('chunk_processed', 0)
                #
                # # Clear statistics for big file
                # if chunk_count == chunk_processed:
                #     self.db["big_" + collection_name].files.update_one(
                #         query,
                #         {"$set": {ask_statistics_field_name: {}}}
                #     )
                # Update statistics
                self.db["big_" + collection_name].files.update_one(
                    query,
                    {
                        "$set": {
                            f"{ask_statistics_field_name}.chunk_count": chunk_count,
                            f"{ask_statistics_field_name}.chunk_size": chunk_size
                        },
                        "$inc": {
                            f"{ask_statistics_field_name}.chunk_processed": rep
                        }
                    }
                )
                return

            # current_document = self.db["small_" + collection_name].find_one(query)

            # Clear statistics for small files
            # if current_document:
            # ask_stats = current_document.get(ask_statistics_field_name, {})
            # chunk_count = ask_stats.get('chunk_count', 0)
            # chunk_processed = ask_stats.get('chunk_processed', 0)
            #
            # if chunk_count == chunk_processed:
            #     self.db["small_" + collection_name].update_one(
            #         query,
            #         {"$set": {ask_statistics_field_name: {}}}
            #     )

            # Update statistics
            self.db["small_" + collection_name].update_one(
                query,
                {
                    "$set": {
                        f"{ask_statistics_field_name}.chunk_count": chunk_count,
                        f"{ask_statistics_field_name}.chunk_size": chunk_size
                    },
                    "$inc": {
                        f"{ask_statistics_field_name}.chunk_processed": rep
                    }
                }
            )

        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)

    def update_processing_status(self, document_id, status_field, status,
                                 collection_name: str = app_common_config.mongo_files_collection_name):
        """Update the 'processing status' field of a document in MongoDB.

        Args:
        processing_status : int - New status of document.
        document_id : str - The _id of the document.

        """
        try:
            fs = GridFS(database=self.db, collection="big_" + collection_name)
            file = fs.find_one({"_id": ObjectId(document_id)})
            if file:
                self.db["big_" + collection_name].files.update_one(
                    {"_id": ObjectId(document_id)},
                    {"$set": {status_field: status}}
                )
                return

            # Update small file
            self.db["small_" + collection_name].update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {status_field: status}}
            )

        except Exception as e:
            message = f"Something went wrong: {e}"
            logger.exception(msg=message)
