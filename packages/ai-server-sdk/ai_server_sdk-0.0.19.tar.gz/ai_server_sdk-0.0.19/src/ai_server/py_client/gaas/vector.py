from typing import List, Dict, Optional
import json
import logging
from ai_server.server_resources.server_proxy import ServerProxy

logger: logging.Logger = logging.getLogger(__name__)


class VectorEngine(ServerProxy):
    """Python class to interact with Vector Database Engines defined in CFG AI"""

    engine_type = "VECTOR"

    def __init__(
        self,
        engine_id: str,
        insight_id: Optional[str] = None,
    ):
        super().__init__()
        self.engine_id = engine_id
        self.insight_id = insight_id

        logger.info("VectorEngine initialized with engine id " + engine_id)

    def addDocument(
        self,
        file_paths: List[str],
        param_dict: Optional[Dict] = {},
        insight_id: Optional[str] = None,
    ) -> bool:
        """
        This method is used to add documents to a vector database. The engine itself will determine how the the documents are
        processed and the embeddings are created.

        Args:
            file_paths (`List[str]`): List of local files paths to push to the server and index.
            param_dict (`Optional[Dict]`): Additional parameters the engine might need to process the documents.
            insight_id (`Optional[str]`): The insight ID to upload the documents to and process the request. Default is to use the clients current insight.
        """
        if insight_id is None:
            if self.insight_id is None:
                insight_id = self.insight_id
            else:
                insight_id = self.server.cur_insight

        assert self.server is not None
        insight_files = self.server.upload_files(
            files=file_paths,
            insight_id=insight_id,
        )

        pixel = (
            'CreateEmbeddingsFromDocuments(engine="'
            + self.engine_id
            + '", filePaths='
            + json.dumps(insight_files)
        )

        if len(param_dict) != 0:
            pixel += ", paramValues = " + json.dumps(param_dict)

        pixel += ");"

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def addVectorCSVFile(
        self,
        file_paths: List[str],
        param_dict: Optional[Dict] = {},
        insight_id: Optional[str] = None,
    ) -> bool:
        """
        Add the vector csv file format documents into the vector database

        Args:
            file_paths (`List[str]`):  The paths (relative to the insight_id) of the files to add
            param_dict (`dict`): A dictionary with optional parameters for listing the documents (index class for FAISS as an example)
            insight_id (`Optional[str]`): Unique identifier for the temporal worksapce where actions are being isolated
        """
        assert file_paths is not None
        if insight_id is None:
            insight_id = self.insight_id

        optionalParams = (
            f",paramValues=[{param_dict}]" if param_dict is not None else ""
        )

        pixel = f'CreateEmbeddingsFromVectorCSVFile(engine="{self.engine_id}",filePaths={file_paths}{optionalParams});'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def removeDocument(
        self,
        file_names: List[str],
        param_dict: Optional[Dict] = {},
        insight_id: Optional[str] = None,
    ) -> bool:
        """
        Remove the documents from the vector database

        Args:
            file_names (`List[str]`):  The names of the files to remove
            param_dict (`dict`): A dictionary with optional parameters for listing the documents (index class for FAISS as an example)
            insight_id (`Optional[str]`): Unique identifier for the temporal worksapce where actions are being isolated
        """
        assert file_names is not None
        if insight_id is None:
            insight_id = self.insight_id

        optionalParams = (
            f",paramValues=[{param_dict}]" if param_dict is not None else ""
        )

        pixel = f'RemoveDocumentFromVectorDatabase(engine="{self.engine_id}",fileNames={file_names}{optionalParams});'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def nearestNeighbor(
        self,
        search_statement: str,
        limit: Optional[int] = 5,
        filters: Optional[Dict] | Optional[str] = None,
        filters_str: Optional[str] = None,
        metafilters: Optional[Dict] | Optional[str] = None,
        metafilters_str: Optional[str] = None,
        param_dict: Optional[Dict] = {},
        insight_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Perform a nearest neighbor or semantic search against a vector database. The searchStatement will be
        converted to a vector using the same embedding model utilized to create the document(s) embeddings.

        Args:
            search_statement (`str`): The statement to search for semantic matches in the vector database
            limit (`Optional[int]`): The amount of top matches to return
            filters (`Optional[Dict]`): A dictionary of filters to apply to the search results
            filters_str (`Optional[str]`): A string of filters to apply to the search results
            metafilters (`Optional[Dict]`): A dictionary of metafilters to apply to the search results
            metafilters_str (`Optional[str]`): A string of metafilters to apply to the search results
            param_dict (`Optional[Dict]`): Additional parameters the engine might need to remove the documents.
            insight_id (`Optional[str]`): The insight ID to upload the documents to and process the request. Default is to use the clients current insight.

        Returns:
            `List[Dict]`: A list of dictionaries that contain the top semantic matches against the search statement
        """

        if insight_id is None:
            if self.insight_id is None:
                insight_id = self.insight_id
            else:
                insight_id = self.server.cur_insight

        pixel = f'VectorDatabaseQuery(engine = "{self.engine_id}", command = ["<e>{search_statement}</e>"], limit = {limit}'

        # 1. Check if filters_str parameter is provided (if so use this)
        # 2. If not, check if filters parameter is provided and check if it is a string (if so use this)
        # 3. If not, check if filters parameter is provided and check if it is a dictionary (if so build the string)
        optional_filters = ""
        if filters_str is not None:
            optional_filters = f",filters=[{filters_str}]"
        if filters is not None and optional_filters == "":
            if isinstance(filters, str):
                optional_filters = f",filters=[{filters}]"
            elif isinstance(filters, dict):
                filter_conditions = []
                for key, value in filters.items():
                    formatted_key = key.capitalize()
                    if isinstance(value, str):
                        formatted_values = f'"{value}"'
                    else:
                        formatted_values = ", ".join([f'"{v}"' for v in value])
                    filter_conditions.append(f"{formatted_key} == [{formatted_values}]")

                optional_filters = (
                    f",filters = [ Filter({', '.join(filter_conditions)})]"
                    if filter_conditions
                    else ""
                )

            else:
                raise ValueError(
                    "Invalid filters type. Filter must be string or dictionary"
                )

        # 1. Check if metafilters_str parameter is provided (if so use this)
        # 2. If not, check if metafilters parameter is provided and check if it is a string (if so use this)
        # 3. If not, check if metafilters parameter is provided and check if it is a dictionary (if so build the string)
        optional_meta_filters = ""
        if metafilters_str is not None:
            optional_meta_filters = f",metaFilters=[{metafilters_str}]"
        if metafilters is not None and optional_meta_filters == "":
            if isinstance(metafilters, str):
                optional_meta_filters = f",metaFilters=[{metafilters}]"
            elif isinstance(metafilters, dict):
                metafilter_conditions = []
                for key, value in metafilters.items():
                    formatted_key = key.capitalize()
                    if isinstance(value, str):
                        formatted_values = f'"{value}"'
                    else:
                        formatted_values = ", ".join([f'"{v}"' for v in value])
                    metafilter_conditions.append(
                        f"{formatted_key} == [{formatted_values}]"
                    )

                optional_meta_filters = (
                    f",metaFilters = [ Filter({', '.join(metafilter_conditions)})]"
                    if metafilter_conditions
                    else ""
                )

            else:
                raise ValueError(
                    "Invalid metafilters type. Metafilters must be string or dictionary"
                )

        pixel += optional_filters + optional_meta_filters

        if len(param_dict) != 0:
            pixel += ", paramValues = " + json.dumps(param_dict)

        pixel += ");"

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def listDocuments(
        self,
        param_dict: Optional[Dict] = {},
        insight_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        List the documents in the vector database

        Args:
            param_dict (`dict`): A dictionary with optional parameters for listing the documents (index class for FAISS as an example)
            insight_id (`Optional[str]`): Unique identifier for the temporal worksapce where actions are being isolated
        """
        if insight_id is None:
            insight_id = self.insight_id

        optionalParams = (
            f",paramValues=[{param_dict}]" if param_dict is not None else ""
        )

        pixel = (
            f'ListDocumentsInVectorDatabase(engine="{self.engine_id}"{optionalParams});'
        )

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def to_langchain_vector_store(self):
        from langchain_core.callbacks import CallbackManagerForRetrieverRun
        from langchain_core.documents import Document
        from langchain_core.retrievers import BaseRetriever

        class VectorStoreCfgAI(BaseRetriever):
            engine_id: str
            vector_engine: VectorEngine
            insight_id: Optional[str]

            def __init__(self, vector_engine):
                super().__init__(
                    engine_id=vector_engine.engine_id,
                    insight_id=vector_engine.insight_id,
                    vector_engine=vector_engine,
                )

            def add_documents(self, file_paths: List[str]):
                """Adds documents to the vector store.

                Args:
                    file_paths (List[str]): Path to documents
                """
                self.vector_engine.addDocument(
                    file_paths=file_paths, insight_id=self.insight_id
                )

            def similarity_search(self, query: str, limit: int) -> List[Document]:
                """Performs a similarity search on the vector store using the given query.

                Args:
                    query (str): Query to search
                    limit (int): Maximum number of nearest neighbor results to be returned

                Returns:
                    List[Document]:  A list of the top `k` most similar documents to the query.
                    Each document contains the page content and metadata associated with
                    the corresponding search result.
                """
                results = self.vector_engine.nearestNeighbor(
                    search_statement=query, limit=limit, insight_id=self.insight_id
                )

                documents = [
                    Document(page_content=result["Content"], metadata=result)
                    for result in results
                ]
                return documents

            def _get_relevant_documents(
                self, query: str, *, run_manager: CallbackManagerForRetrieverRun
            ) -> List[Document]:
                return self.similarity_search(query)

            @property
            def _llm_type(self) -> str:
                """Return type of chat model."""
                return "CFG AI"

        return VectorStoreCfgAI(vector_engine=self)
