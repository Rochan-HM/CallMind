from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Any
import chromadb
from chromadb.config import Settings

# Define the request and response models
class ContextRequest(BaseModel):
    query: str
    top_k: int = 5  # Number of results to return (optional, default 5)

class ContextChunk(BaseModel):
    id: str
    text: str
    metadata: dict = {}

class ContextResponse(BaseModel):
    context: List[ContextChunk]

# Initialize FastAPI app
app = FastAPI(title="MCP Server Template with ChromaDB")

# Initialize ChromaDB client (assumes local ChromaDB instance)
chroma_client = chromadb.Client(Settings())
# Replace 'my_collection' with your actual collection name
collection = chroma_client.get_or_create_collection(name="my_collection")

@app.post("/v1/context", response_model=ContextResponse)
async def get_context(request: ContextRequest):
    """
    MCP context endpoint: Accepts a query and returns relevant context chunks from ChromaDB.
    """
    try:
        # Perform similarity search in ChromaDB
        results = collection.query(
            query_texts=[request.query],
            n_results=request.top_k
        )
        # Format results for MCP
        context_chunks = []
        for idx, doc_id in enumerate(results.get("ids", [[]])[0]):
            chunk = ContextChunk(
                id=doc_id,
                text=results["documents"][0][idx],
                metadata=results.get("metadatas", [[]])[0][idx] if results.get("metadatas") else {}
            )
            context_chunks.append(chunk)
        return ContextResponse(context=context_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChromaDB query failed: {str(e)}")

# To run: uvicorn mcp_server.callmind_mcp:app --reload
