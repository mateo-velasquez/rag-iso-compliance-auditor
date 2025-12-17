from fastapi import FastAPI
from app.api.routers import audit, health

def create_app():
    app = FastAPI()
    
    app.include_router(audit.router, prefix="/clio")
    app.include_router(health.router, prefix="/clio")

    return app