from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.business.orchestrator import AuditOrchestrator
from app.schemas.audit import (
    DocumentUploadRequest,
    DocumentUploadResponse
)

# Creamos el router específico
router = APIRouter(
    prefix="/audit",
    tags=["Audit Operations"] # Esto organiza el Swagger
)

def get_orchestrator():
    return AuditOrchestrator()

# -------------------------------- ENDPOINTS ------------------------------------------#

# Endpoint para subir un PDF, lo guarde localmente y registre su metadata en Mongo.
@router.post("/upload-pdf", tags=["Files"], response_model=DocumentUploadResponse, status_code=201)
async def upload_document_pdf(
    file: UploadFile = File(...),
    orchestrator: AuditOrchestrator = Depends(get_orchestrator)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="Solo se permiten archivos PDF")
        
    return await orchestrator.handle_upload(file)

# Endpoint para obtener un documento por su ID
@router.get("/document/:id", status_code=200)
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para borrar un archivo por su ID
@router.delete("/document/:id", status_code=204)
def delete_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para cambiar un archivo por su ID
@router.patch("/document/:id", status_code=200)
def patch_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para obtener todos los archivos (información)
@router.get("/documents", status_code=200)
def get_documents():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint del Chatbot: Responde preguntas usando contexto ISO + Docs Usuario.
@router.post("/ask", status_code=201)
def ask_cleo():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para Buscador semántico puro sobre la norma ISO (Para verificar fuentes).
@router.post("/search", status_code=201)
def find_data_ISO():
    return {"status": "operational", "service": "iso-auditor-rag"}
