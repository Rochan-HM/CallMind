from fastmcp import FastMCP
from pydantic import BaseModel
import os
import sys

# Append the path to the chromadb_utils package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chromadb_utils.utils import retrieve_document

mcp = FastMCP("Callmind 📞")


class QueryCollectionResponse(BaseModel):
    result: list[str]


@mcp.tool
def query_collection(query: str) -> QueryCollectionResponse:
    """Query the collection"""
    chroma_result = retrieve_document(query)

    (
        x := QueryCollectionResponse(
            result=[
                transcription[0]
                for transcription in chroma_result["documents"]
                if transcription[0] is not None
            ]
        )
    )

    return x


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)
