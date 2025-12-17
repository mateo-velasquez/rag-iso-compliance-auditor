from fastapi import APIRouter

router = APIRouter(
    tags=["System"]
)

# Endpoint para Check de estado.
@router.get("/health")
def health_check():
    return {"status": "operational", "service": "iso-auditor-rag"}
