from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Upload / Delete
class DocumentResponse(BaseModel):
    message: str = Field(..., description="Mensaje de confirmación de la operación")
    document_id: str = Field(..., description="ID único del documento afectado")


# get y gets
class DocumentResponseComplete(BaseModel):
    id: str = Field(..., description="ID de MongoDB convertido a string")
    # Metadata del archivo físico
    filename: str = Field(..., description="Nombre original del archivo")
    file_path: str = Field(..., description="Ruta interna de almacenamiento")
    file_hash: str = Field(..., description="Hash SHA-256 para deduplicación")
    upload_date: datetime = Field(..., description="Fecha de carga original")
    update_date: datetime = Field(..., description="Fecha de la última modificación")
    # Metadata de Negocio (RAG / ISO)
    iso_version_target: str = Field(default="2022", description="Versión de la norma ISO asociada")
    # Literal restringe el campo a solo estas opciones válidas
    doc_type: Literal["policy", "procedure", "evidence", "other"] = Field(
        default="other", 
        description="Tipo de documento según la norma"
    )
    # Estado del procesamiento
    status: Literal["pending", "processed", "error"] = Field(
        default="pending", 
        description="Estado actual del procesamiento de embeddings"
    )