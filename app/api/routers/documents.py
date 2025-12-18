from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body
from app.business.document_manager import DocumentManager
from app.core.logger import Logger
from app.schemas.documents import (
    DocumentResponse, 
    DocumentResponseComplete
)

# Creamos el router específico
router = APIRouter(
    prefix="/documents",
    tags=["Documents Operations"] # Esto organiza el Swagger
)

# Inyección de dependencias
def get_document_manager():
    return DocumentManager()

# -------------------------------- ENDPOINTS ------------------------------------------#

# Endpoint para Subir PDF
@router.post("/upload-pdf", response_model=DocumentResponse, status_code=201)
async def upload_document_pdf(
    file: UploadFile = File(...),
    documentManager: DocumentManager = Depends(get_document_manager)
):
    # Validación básica de extensión
    if not file.filename.lower().endswith(".pdf"):
        Logger.add_to_log("error", "Intento de subir archivo no PDF")
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
    # Llamamos al manager (await es obligatorio aquí)
    return await documentManager.handle_upload(file)


# Endpoint Obtener todos los documentos
@router.get("/documents", response_model=List[DocumentResponseComplete], status_code=200)
async def get_documents(
    documentManager: DocumentManager = Depends(get_document_manager)
):
    return await documentManager.get_all_documents()


# Endpoint para obtener documento por id
@router.get("/document/{document_id}", response_model=DocumentResponseComplete, status_code=200)
async def get_document_by_id(
    document_id: str, 
    documentManager: DocumentManager = Depends(get_document_manager)
):
    if document_id == "":
        Logger.add_to_log("error", "Debe colocar un id válido en el método")
        raise HTTPException(status_code=404, detail="Debe colocar un id no vacío")
    return await documentManager.get_document_by_id(document_id)


# Endpoint de borrado de documento por id
@router.delete("/document/{document_id}", response_model=DocumentResponse, status_code=200)
async def delete_document_by_id(
    document_id: str,
    documentManager: DocumentManager = Depends(get_document_manager)
):
    if document_id == "":
        Logger.add_to_log("error", "Debe colocar un id válido en el método")
        raise HTTPException(status_code=404, detail="Debe colocar un id no vacío")
    return await documentManager.delete_document(document_id)
