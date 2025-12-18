from fastapi import FastAPI
from app.api.routers import audit, health, documents

def create_app():
    app = FastAPI()
    
    app.include_router(audit.router, prefix="/cleo")
    app.include_router(health.router, prefix="/cleo")
    app.include_router(documents.router, prefix="/cleo")

    return app