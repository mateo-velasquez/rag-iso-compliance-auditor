from typing import Tuple, List, Dict
from app.core.logger import Logger
from app.services.external.llm_factory import LLMFactory
from app.db.repository.vector_repo import vector_repo
from app.core.constants import systemsPrompts

# Clase que encapsula el flujo RAG: Retrieval + Augmented Generation.
class RagPipeline:

    def __init__(self):
        # Usamos la Factory para obtener el cliente
        self.client = LLMFactory.create_cohere_client_v2()
        self.vector_db = vector_repo
        self.model = "command-a-03-2025" # Modelo potente para generación

    # Método que ejecuta el pipeline completo
    async def run(self, question: str) -> Tuple[str, List[Dict], float]:
        Logger.add_to_log("info", "RagPipeline: Iniciando ejecución...")

        # Retrieval (Búsqueda de Contexto)
        retrieved_docs = self.vector_db.search_similarity(question, k=5)

        if not retrieved_docs:
            Logger.add_to_log("warning", "RagPipeline: No se encontró contexto.")
            return "No encontré información relevante en los documentos cargados para responder tu consulta.", [], 0.0
        
        top_similarity_score = retrieved_docs[0].get('similarity_score', 0.0)

        # Convertimos la lista de dicts en un solo string de texto
        context_text = "\n\n---\n\n".join(
            [f"Documento: {doc['title']}\nContenido: {doc['content_snippet']}" for doc in retrieved_docs]
        )

        history_text = ""

        # Definimos el Prompt del Sistema con la personalidad y reglas
        system_prompt = systemsPrompts.system_prompt_RAG(context_text, history_text)

        # Llamada al LLM
        Logger.add_to_log("info", "RagPipeline: Generando respuesta con LLM...")
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.3, # Baja temperatura para ser fiel al texto
                seed=123
            )

            generated_answer = response.message.content[0].text
            
            Logger.add_to_log("info", "RagPipeline: Respuesta generada con éxito.")
            return generated_answer, retrieved_docs, top_similarity_score

        except Exception as e:
            Logger.add_to_log("error", f"RagPipeline: Error generando respuesta: {e}")
            return "Hubo un error técnico al generar la respuesta.", [], 0.0