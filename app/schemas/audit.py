# Aca se crearan los DTOs correspondientes
from pydantic import BaseModel, Field
from typing import List, Optional

# Validamos que no estén vacíos usando Field

# Embeddings (Generación de Vectores)
class GenerateEmbeddingsRequest(BaseModel):
    document_id: str = Field(..., description="ID del documento a procesar")

class GenerateEmbeddingsResponse(BaseModel):
    message: str
    document_id: str


# Ask (Pregunta al LLM - RAG)
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Pregunta del usuario")

class AskResponse(BaseModel):
    answer: str
    context_used: Optional[str] = Field(None, description="Fragmento de texto usado para responder")
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Score de similitud del contexto (entre 0 y 1)")
    grounded: bool = Field(..., description="Indica si la respuesta se basó en contexto real")