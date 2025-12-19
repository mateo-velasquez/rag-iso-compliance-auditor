import cohere
from app.core.logger import Logger
from app.core.config import settings

class LLMFactory:
    _client_instance = None

    # Crea y retorna una instancia del cliente Cohere V2: Implementa un patrón Singleton simple para reutilizar la conexión.
    @staticmethod
    def create_cohere_client_v2() -> cohere.ClientV2:
        if LLMFactory._client_instance is None:
            api_key = settings.api_key
            if not api_key:
                Logger.add_to_log("critical", "LLMFactory: No se encontró COHERE_API_KEY.")
                raise ValueError("COHERE_API_KEY no configurada.")
            
            try:
                # Instanciamos el cliente una sola vez
                LLMFactory._client_instance = cohere.ClientV2(api_key=api_key)
                Logger.add_to_log("info", "LLMFactory: Cliente Cohere V2 inicializado.")
            except Exception as e:
                Logger.add_to_log("critical", f"LLMFactory: Error conectando con Cohere: {e}")
                raise e
        
        return LLMFactory._client_instance

llm_factory = LLMFactory()