import cohere
from app.core.config import settings
from app.core.logger import Logger

class EmbeddingService:
    def __init__(self):
        # Inicializamos el cliente una sola vez
        self.api_key = settings.api_key
        self.client = cohere.ClientV2(api_key=self.api_key)
        self.model = "embed-multilingual-v3.0"

    # Recibe el texto y genera los embeddings
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        # Agregué procesamiento por lotes
        try:
            # Eliminamos vacíos por seguridad
            valid_texts = [t for t in texts if t and t.strip()]
            if not valid_texts:
                return []
            
            # Comienzo con el procesamiento en lotes
            BATCH_SIZE = 90 # Usamos 90 para tener margen (Límite es 96)
            all_embeddings = []

            # Iteramos de 90 en 90
            # range(inicio, fin, paso) -> 0, 90, 180...
            for i in range(0, len(valid_texts), BATCH_SIZE):
                # Cortamos el lote actual (slicing)
                batch = valid_texts[i : i + BATCH_SIZE]
                
                Logger.add_to_log("info", f"Enviando lote a Cohere: {len(batch)} textos...")
                
                # Llamada a la API solo con este grupito
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document",
                    embedding_types=["float"]
                )
                
                # Acumulamos los resultados en la lista principal
                all_embeddings.extend(response.embeddings.float_)

            Logger.add_to_log("info", f"Total de embeddings generados: {len(all_embeddings)}")
            return all_embeddings

        except Exception as e:
            Logger.add_to_log("error", f"Error generando embeddings con Cohere: {e}")
            raise e

# Instancia global para importar en otros lados
embedding_service = EmbeddingService()