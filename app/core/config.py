# Archivo con las variables de entorno
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class Settings:
    def __init__(self):
        # Variables de mongo
        self.MONGO_HOST = os.getenv("POLKO_MONGO_HOST") # Variable que contiene El host
        self.MONGO_PORT = os.getenv("POLKO_MONGO_PORT") # Variable que contiene el puerto dónde se conecta la DB
        self.MONGO_USER = os.getenv("POLKO_MONGO_USER") # Variable que contiene el usuario de la BD
        self.MONGO_PASS = os.getenv("POLKO_MONGO_PASS") # Variable que contiene la contraseña de la BD
        self.MONGO_DB   = os.getenv("POLKO_MONGO_DB") # Variable que contiene el nombre de la BD

        # Variables de Cohere 
        self.api_key = os.getenv("COHERE_API_KEY") # Variable con la clave para el Cohere
