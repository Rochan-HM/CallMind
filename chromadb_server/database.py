import os
import uuid
from typing import List, Optional
from datetime import datetime

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from models import (
    CollectionInfo,
    DocumentModel,
    QueryModel,
    UpdateDocumentModel,
    DocumentResponse,
)

from dotenv import load_dotenv

load_dotenv()

GOOGLE_EMBEDDING_FUNCTION = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ChromaDB Client Manager
class ChromaDBManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB with persistent storage."""
        self.persist_directory = persist_directory

        # Ensure the directory exists
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Default collection
        self.default_collection_name = "default"

    def get_or_create_collection(self, collection_name: str = None):
        """Get or create a collection."""
        name = collection_name or self.default_collection_name
        return self.client.get_or_create_collection(
            name=name, embedding_function=GOOGLE_EMBEDDING_FUNCTION
        )

    def list_collections(self) -> List[CollectionInfo]:
        """List all collections."""
        collections = self.client.list_collections()
        result = []
        for collection in collections:
            coll_obj = self.client.get_collection(collection.name)
            result.append(
                CollectionInfo(
                    name=collection.name,
                    count=coll_obj.count(),
                    metadata=collection.metadata,
                )
            )
        return result

    def add_document(self, collection_name: str, document: DocumentModel) -> str:
        """Add a document to a collection."""
        collection = self.get_or_create_collection(collection_name)

        # Generate ID if not provided
        doc_id = document.id or str(uuid.uuid4())

        # Prepare metadata
        metadata = document.metadata or {}
        metadata["created_at"] = datetime.now().isoformat()

        # Add document
        collection.add(documents=[document.content], metadatas=[metadata], ids=[doc_id])

        return doc_id

    def query_documents(
        self, collection_name: str, query: QueryModel
    ) -> List[DocumentResponse]:
        """Query documents from a collection."""
        collection = self.get_or_create_collection(collection_name)

        # Perform query
        results = collection.query(
            query_texts=[query.query], n_results=query.n_results, where=query.where
        )

        # Format response
        documents = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                documents.append(
                    DocumentResponse(
                        id=results["ids"][0][i],
                        content=results["documents"][0][i],
                        metadata=(
                            results["metadatas"][0][i]
                            if results["metadatas"][0]
                            else {}
                        ),
                        distance=(
                            results["distances"][0][i] if results["distances"] else None
                        ),
                    )
                )

        return documents

    def get_document(
        self, collection_name: str, document_id: str
    ) -> Optional[DocumentResponse]:
        """Get a specific document by ID."""
        collection = self.get_or_create_collection(collection_name)

        try:
            results = collection.get(ids=[document_id])
            if results["documents"]:
                return DocumentResponse(
                    id=results["ids"][0],
                    content=results["documents"][0],
                    metadata=results["metadatas"][0] if results["metadatas"] else {},
                )
        except Exception:
            pass

        return None

    def update_document(
        self, collection_name: str, document_id: str, update_data: UpdateDocumentModel
    ) -> bool:
        """Update a document."""
        collection = self.get_or_create_collection(collection_name)

        try:
            # Get existing document
            existing = collection.get(ids=[document_id])
            if not existing["documents"]:
                return False

            # Prepare update data
            new_content = update_data.content or existing["documents"][0]
            new_metadata = (
                update_data.metadata or existing["metadatas"][0]
                if existing["metadatas"]
                else {}
            )
            new_metadata["updated_at"] = datetime.now().isoformat()

            # Update document
            collection.update(
                ids=[document_id], documents=[new_content], metadatas=[new_metadata]
            )

            return True
        except Exception:
            return False

    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document."""
        collection = self.get_or_create_collection(collection_name)

        try:
            collection.delete(ids=[document_id])
            return True
        except Exception:
            return False

    def delete_collection(self, collection_name: str) -> bool:
        """Delete an entire collection."""
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception:
            return False


# Initialize ChromaDB manager
chroma_manager = ChromaDBManager()
