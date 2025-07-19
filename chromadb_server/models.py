from typing import Optional, Dict, Any
from pydantic import BaseModel


# Pydantic models for API requests and responses
class DocumentModel(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class QueryModel(BaseModel):
    query: str
    n_results: Optional[int] = 5
    where: Optional[Dict[str, Any]] = None


class UpdateDocumentModel(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None


class CollectionInfo(BaseModel):
    name: str
    count: int
    metadata: Optional[Dict[str, Any]] = None
