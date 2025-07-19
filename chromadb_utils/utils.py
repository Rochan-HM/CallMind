import chromadb
import os
from chromadbx import UUIDGenerator
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
from typing import Any, Optional

load_dotenv()

client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database="testdb",
)

google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.getenv("GEMINI_API_KEY"),
)
collection = client.get_or_create_collection("callmind", embedding_function=google_ef)


def add_document(document: str, metadata: Optional[dict[str, Any]] = None):
    collection.add(
        documents=[document],
        ids=UUIDGenerator().generate_uuid(),
        metadata=metadata,
    )


def retrieve_document(query: str, **kwargs):
    return collection.query(
        query_texts=[query],
        **kwargs,
    )
