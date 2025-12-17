from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid

# Clase de Documento para MongoDB
class DocumentDAO(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id") # Generamos un UUID automático si no viene uno.
    filename: str
    file_path: str
    file_hash: str
    upload_date: datetime = Field(default_factory=datetime.now)
    update_date: datetime = Field(default_factory=datetime.now)
    # Metadata RAG
    iso_version_target: str = "2022"  # Valor por defecto
    doc_type: Literal["policy", "procedure", "evidence", "other"] = "other" # Validamos opciones
    # Estado
    status: Literal["pending", "processed", "error"] = "pending"
    error_msg: Optional[str] = None # Solo se llena si hay error
    # Soft Delete
    is_active: bool = True
    deleted_date: Optional[datetime] = None