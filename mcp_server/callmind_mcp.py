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
                transcription
                for index, transcription in enumerate(chroma_result["documents"][0])
                if transcription[0] is not None and chroma_result["distances"][0][index] >= 0.75
            ]
        )
    )

    return x


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)
