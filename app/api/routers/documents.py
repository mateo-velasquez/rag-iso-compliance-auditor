from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.business.orchestrator import AuditOrchestrator
from app.business.document_manager import DocumentManager
from app.core.logger import Logger
from app.schemas.audit import (
    DocumentUploadRequest,
    DocumentUploadResponse
)

# Creamos el router específico
router = APIRouter(
    prefix="/documents",
    tags=["Documents Operations"] # Esto organiza el Swagger
)

def get_document_manager():
    return DocumentManager()

# -------------------------------- ENDPOINTS ------------------------------------------#

# Endpoint para subir un PDF, lo guarde localmente y registre su metadata en Mongo.
@router.post("/upload-pdf", tags=["Files"], response_model=DocumentUploadResponse, status_code=201)
async def upload_document_pdf(
    file: UploadFile = File(...),
    documentManager: DocumentManager = Depends(get_document_manager)
):
    if not file.filename.endswith(".pdf"):
        Logger.add_to_log("error", "No se pudo insertar el documento por no ser un PDF")
        raise HTTPException(status_code=404, detail="Solo se permiten archivos PDF")
        
    return await documentManager.handle_upload(file)

# Endpoint para obtener un documento por su ID
@router.get("/document/{document_id}", status_code=200)
def get_document_by_id(
    document_id: str, 
    documentManager: DocumentManager = Depends(get_document_manager)
):
    if document_id == None:
        Logger.add_to_log("error", "ID enviado vacío en Método: get_document_by_id()")
        raise HTTPException(status_code=404, detail="Debe enviar un id válido")
    
    return #await documentManager.handle_get_document_by_id(document_id)

# Endpoint para borrar un archivo por su ID
@router.delete("/document/{document_id}", status_code=204)
def delete_document_by_id(document_id):
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para cambiar un archivo por su ID
@router.patch("/document/{document_id}", status_code=200)
def patch_document_by_id(document_id):
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para obtener todos los archivos (información)
@router.get("/documents", status_code=200)
def get_documents():
    return {"status": "operational", "service": "iso-auditor-rag"}