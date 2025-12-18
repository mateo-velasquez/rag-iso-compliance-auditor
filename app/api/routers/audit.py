from fastapi import APIRouter
from app.business.orchestrator import AuditOrchestrator
from app.core.logger import Logger

# Creamos el router específico
router = APIRouter(
    prefix="/audit",
    tags=["Audit Operations"] # Esto organiza el Swagger
)

def get_orchestrator():
    return AuditOrchestrator()

# -------------------------------- ENDPOINTS ------------------------------------------#

# Endpoint del Chatbot: Responde preguntas usando contexto ISO + Docs Usuario.
@router.post("/ask", status_code=201)
def ask_cleo():
    return {"status": "operational", "service": "iso-auditor-rag"}

# Endpoint para Buscador semántico puro sobre la norma ISO (Para verificar fuentes).
@router.post("/search", status_code=201)
def find_data_ISO():
    return {"status": "operational", "service": "iso-auditor-rag"}
