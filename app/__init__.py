from fastapi import FastAPI
from app.api.routers import audit, health

def create_app():
    app = FastAPI()
    
    app.include_router(audit.router, prefix="/cleo")
    app.include_router(health.router, prefix="/cleo")

    return app