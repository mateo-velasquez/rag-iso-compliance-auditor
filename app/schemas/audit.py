# Aca se crearan los DTOs correspondientes
from pydantic import BaseModel, Field
from typing import List, Optional

# Validamos que no estén vacíos usando Field

# Upload
class DocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Título del documento") 

class DocumentUploadResponse(BaseModel):
    message: str = Field(..., description="Mensaje de confirmación")
    document_id: str = Field(..., description="ID único del documento generado")


# Embeddings (Generación de Vectores)
class GenerateEmbeddingsRequest(BaseModel):
    document_id: str = Field(..., description="ID del documento a procesar")

class GenerateEmbeddingsResponse(BaseModel):
    message: str
    document_id: str


# Search (Búsqueda Semántica)
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Consulta del usuario")

# Este es un subobjeto para la lista de resultados
class SearchResultItem(BaseModel):
    document_id: str
    title: str
    content_snippet: str
    similarity_score: float = Field(None, ge=0.0, le=1.0, description="Score de similitud del contexto (entre 0 y 1)")

class SearchResponse(BaseModel):
    results: List[SearchResultItem]


# Ask (Pregunta al LLM - RAG)
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Pregunta del usuario")

class AskResponse(BaseModel):
    answer: str
    context_used: Optional[str] = Field(None, description="Fragmento de texto usado para responder")
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Score de similitud del contexto (entre 0 y 1)")
    grounded: bool = Field(..., description="Indica si la respuesta se basó en contexto real")