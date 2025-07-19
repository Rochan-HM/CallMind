import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database="testdb",
)

collection = client.get_or_create_collection("callmind")


def retrieve_document(query: str, **kwargs):
    return collection.query(
        query_texts=[query],
        n_results=1,
        **kwargs,
    )
