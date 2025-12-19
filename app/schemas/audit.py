# Aca se crearan los DTOs correspondientes
from pydantic import BaseModel, Field
from typing import List, Optional

# Modelo para la entrada de la búsqueda (Request)
class SearchQuery(BaseModel):
    query: str      # La pregunta o término a buscar
    k: int = 3      # Cantidad de resultados deseados (Top-K)

# Modelo para cada resultado encontrado (Response Item)
class SearchResult(BaseModel):
    document_id: str
    filename: str
    content_snippet: str
    similarity_score: float

# Modelo para la respuesta de la auditoría (Chatbot) - Placeholder para futuro
class AuditResponse(BaseModel):
    answer: str
    sources: List[SearchResult] = []


# Ask (Pregunta al LLM - RAG)
class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Pregunta del usuario")

class AskResponse(BaseModel):
    answer: str
    context_used: Optional[str] = Field(None, description="Fragmento de texto usado para responder")
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Score de similitud del contexto (entre 0 y 1)")
    grounded: bool = Field(..., description="Indica si la respuesta se basó en contexto real")