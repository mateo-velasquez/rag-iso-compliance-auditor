import uvicorn
from app import create_app
from fastapi.middleware.cors import CORSMiddleware

app = create_app()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se pone el dominio real, para pruebas "*" está bien
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

