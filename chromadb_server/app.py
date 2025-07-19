#!/usr/bin/env python3
"""
Simple script to run the ChromaDB FastAPI server.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from typing import List
from database import chroma_manager
from models import (
    CollectionInfo,
    DocumentModel,
    QueryModel,
    DocumentResponse,
    UpdateDocumentModel,
)

# FastAPI app
app = FastAPI(
    title="ChromaDB API",
    description="ChromaDB Vector Database API with persistent storage",
    version="1.0.0",
)


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "ChromaDB API is running", "status": "healthy"}


@app.get("/collections", response_model=List[CollectionInfo])
async def list_collections():
    """List all collections."""
    return chroma_manager.list_collections()


@app.post("/collections/{collection_name}/documents")
async def add_document(collection_name: str, document: DocumentModel):
    """Add a document to a collection."""
    try:
        doc_id = chroma_manager.add_document(collection_name, document)
        return {"id": doc_id, "message": "Document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")


@app.post("/collections/{collection_name}/query", response_model=List[DocumentResponse])
async def query_documents(collection_name: str, query: QueryModel):
    """Query documents from a collection."""
    try:
        results = chroma_manager.query_documents(collection_name, query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error querying documents: {str(e)}"
        )


@app.get(
    "/collections/{collection_name}/documents/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(collection_name: str, document_id: str):
    """Get a specific document by ID."""
    document = chroma_manager.get_document(collection_name, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.put("/collections/{collection_name}/documents/{document_id}")
async def update_document(
    collection_name: str, document_id: str, update_data: UpdateDocumentModel
):
    """Update a document."""
    success = chroma_manager.update_document(collection_name, document_id, update_data)
    if not success:
        raise HTTPException(
            status_code=404, detail="Document not found or update failed"
        )
    return {"message": "Document updated successfully"}


@app.delete("/collections/{collection_name}/documents/{document_id}")
async def delete_document(collection_name: str, document_id: str):
    """Delete a document."""
    success = chroma_manager.delete_document(collection_name, document_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Document not found or deletion failed"
        )
    return {"message": "Document deleted successfully"}


@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete an entire collection."""
    success = chroma_manager.delete_collection(collection_name)
    if not success:
        raise HTTPException(
            status_code=404, detail="Collection not found or deletion failed"
        )
    return {"message": "Collection deleted successfully"}


@app.get("/collections/{collection_name}/count")
async def get_collection_count(collection_name: str):
    """Get the number of documents in a collection."""
    try:
        collection = chroma_manager.get_or_create_collection(collection_name)
        count = collection.count()
        return {"collection": collection_name, "count": count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting collection count: {str(e)}"
        )


if __name__ == "__main__":
    print("🚀 Starting ChromaDB API server...")
    print("📚 API Documentation will be available at: http://localhost:8501/docs")
    print("🔍 Interactive API at: http://localhost:8501/redoc")

    uvicorn.run(
        "app:app",  # Use import string format for proper reload
        host="0.0.0.0",
        port=8501,
        reload=True,  # Enable auto-reload for development
        log_level="info",
    )
