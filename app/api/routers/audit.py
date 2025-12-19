from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.business.orchestrator import AuditOrchestrator
from app.schemas.audit import SearchQuery, SearchResult

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
async def ask_cleo(
    query_params: SearchQuery, 
    orchestrator: AuditOrchestrator = Depends(get_orchestrator)
):
    # Delegamos al orquestador la lógica compleja del RAG
    response = await orchestrator.answer_question(query_params.query)
    return response

# Endpoint para Buscador semántico puro sobre la norma ISO (Para verificar fuentes).
@router.post("/search", status_code=201, response_model=List[SearchResult])
async def find_data_ISO(
    search_params: SearchQuery, 
    orchestrator: AuditOrchestrator = Depends(get_orchestrator)
):
    try:
        # Llamamos al método search del orquestador
        results = await orchestrator.perform_search(
            query=search_params.query, 
            k=search_params.k
        )
        return results
        
    except Exception as e:
        # Si algo falla en la lógica de negocio, retornamos un 500 genérico
        raise HTTPException(status_code=500, detail=str(e))