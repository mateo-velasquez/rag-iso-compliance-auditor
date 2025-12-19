import cohere
from app.core.config import settings
from app.core.logger import Logger

class EmbeddingService:
    def __init__(self):
        # Inicializamos el cliente una sola vez
        self.client = cohere.ClientV2(api_key=settings.api_key)
        self.model = "embed-multilingual-v3.0"

    # Recibe el texto y genera los embeddings
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document",
                embedding_types=["float"],
            )
            return response.embeddings.float_
        except Exception as e:
            Logger.add_to_log("error", f"Error generando embeddings con Cohere: {e}")
            raise e

# Instancia global para importar en otros lados
embedding_service = EmbeddingService()