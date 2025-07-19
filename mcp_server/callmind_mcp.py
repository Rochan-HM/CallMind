from fastmcp import FastMCP
import os
import sys

# Append the path to the chromadb_utils package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chromadb_utils.utils import retrieve_document

mcp = FastMCP("Callmind 📞")

@mcp.tool
def query_collection(query: str) -> str:
    """Query the collection"""
    return retrieve_document(query)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)