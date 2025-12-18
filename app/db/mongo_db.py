import motor.motor_asyncio
from app.core.config import settings  
from app.core.logger import Logger 

class MongoConnection:
    _instance = None

    def __new__(cls):
        # Patrón Singleton: Garantiza una única instancia de conexión
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Evitamos re-inicializar si ya existe la conexión
        if self._initialized:
            return

        self.client = None
        self.db = None

        try:
            # Construcción segura de la URI usando settings
            #mongo_uri = (
            #    f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@"
            #    f"{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB_NAME}?authSource=admin"
            #)

            mongo_uri = (
                f"mongodb+srv://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.ATLAS_CONECTION}"
                f"/{settings.MONGO_DB_NAME}?retryWrites=true&w=majority&appName={settings.APPNAME}"
            )
            
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                mongo_uri,
                maxPoolSize=10, 
                minPoolSize=1
            )
            
            self.db = self.client[settings.MONGO_DB_NAME]
            self._initialized = True
            
            Logger.add_to_log("info", f"Conexión a MongoDB iniciada: {settings.MONGO_DB_NAME}")

        except Exception as e:
            Logger.add_to_log("critical", f"Fallo crítico conectando a MongoDB: {e}") # Que falle si no hay db
            raise e

    # Método para cheaquear el endpoint/health
    async def check_connection(self) -> bool:
        try:
            await self.db.command("ping")
            return True
        except Exception as e:
            Logger.add_to_log("error", f"MongoDB Health Check Falló: {e}")
            return False

    # Cerramos la conexión al apagar la app
    def close(self):
        if self.client:
            self.client.close()
            Logger.add_to_log("info", "Conexión a MongoDB cerrada.")

# Instancia Global para importar en otros lados
mongo_manager = MongoConnection()