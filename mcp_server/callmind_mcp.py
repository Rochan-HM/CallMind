import os
import sys

from fastmcp import FastMCP
from pydantic import BaseModel

# Append the path to the chromadb_utils package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chromadb_utils.utils import retrieve_document

mcp = FastMCP("Callmind 📞")


class QueryCollectionResponse(BaseModel):
    result: list[str]


@mcp.tool
def query_collection(query: str) -> QueryCollectionResponse:
    """
    Look up conversations by the user and search for relevant transcripts.

    All of the user's conversations are stored in the database.
    This tool allows you to search for relevant transcripts based on a query.

    Args:
        query: The query to search for.
        The query should be a natural language query.

    Returns:
        A list of relevant transcripts.
    """
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
