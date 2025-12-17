from fastapi import APIRouter

# Creamos el router específico
router = APIRouter(
    prefix="Audit",
    tags=["Audit Operations"] # Esto organiza el Swagger
)


# -------------------------------- ENDPOINTS ------------------------------------------#

# Endpoint para cargar un archivo
@router.post("/document/:id")
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para obtener un documento por su ID
@router.get("/document/:id")
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para borrar un archivo por su ID
@router.delete("/document/:id")
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para cambiar un archivo por su ID
@router.put("/document/:id")
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para obtener todos los archivos (información)
@router.get("/documents")
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint del Chatbot: Responde preguntas usando contexto ISO + Docs Usuario.
@router.post("/ask")
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para Buscador semántico puro sobre la norma ISO (Para verificar fuentes).
@router.post("/search")
def get_document_by_id():
    return {"status": "operational", "service": "iso-auditor-rag"}
