ENTERPRISE_ID = "X"
SERVICE_NAME = "subscr_mgt"
COLLECTION_TYPE_FULL_REPO = "full_doc"
COLLECTION_TYPE_QA = "qa"
COLLECTION_TYPE_MERGED = "merged"

AVAILABLE_COLLECTION_TYPES = [COLLECTION_TYPE_FULL_REPO, COLLECTION_TYPE_QA, COLLECTION_TYPE_MERGED]

FILES_PREFIX = "XSMM_"

RAG_QUERY_MODELS_POOL = [
    "azure/gpt-4o-2024-05-13",
    "azure/gpt-4o-2024-11-20",
    "azure/gpt-4o-mini-2024-07-18",
    "azure/gpt-4-turbo-2024-04-09"
]

# RAG_QUERY_MODELS_POOL = [
#     # "azure/o3-mini-2025-01-31",
#     "azure/o1-2024-12-17",
# ]

NEO4j_URI = "bolt://localhost:7687"
NEO4j_USERNAME = "neo4j"
NEO4j_PASSWORD = "12345678"


def get_collection_name(
        enterprise_id: str,
        service_name: str,
        collection_type: str
) -> str:
    if not enterprise_id or not service_name or not collection_type:
        raise ValueError("enterprise_id, service_name and collection_type must be provided")
    if collection_type not in AVAILABLE_COLLECTION_TYPES:
        raise ValueError(f"collection_type must be one of {AVAILABLE_COLLECTION_TYPES}")

    return f"Enterprise_{enterprise_id}_{service_name}_{collection_type}"
