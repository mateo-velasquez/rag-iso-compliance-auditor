# Archivo para orquestar toda la lógica de negocios
from typing import List
from fastapi import HTTPException
from app.core.logger import Logger
from app.db.repository.vector_repo import vector_repo
from app.schemas.audit import SearchResult 

# Clases Placeholder (De momento lo dejo así para que no falle)
class RagPipeline:
    pass

class Guardrails:
    pass

class AuditOrchestrator:
    def __init__(self):
        # cargamos los otros business
        self.rag_pipeline = RagPipeline()
        self.guardrails = Guardrails()
        self.vector_db = vector_repo

    async def answer_question(self, question: str):
        # 1. Guardrails Input
        # 2. Triage
        # 3. RAG Pipeline
        # 4. Guardrails Output
        pass

    # Método para realizar búsqueda semántica pura: Este método es utilizado para verificar fuentes o debugging
    async def perform_search(self, query: str, k: int) -> List[SearchResult]:
        Logger.add_to_log("info", f"AuditOrchestrator: Iniciando búsqueda para '{query}'")
        
        try:
            # Delegamos la búsqueda al repositorio vectorial
            results = self.vector_db.search_similarity(query, k)
            
            # Mapeamos los resultados crudos (dicts) al Schema de Pydantic: Esto asegura que la API siempre responda con la estructura correcta
            formatted_results = [
                SearchResult(
                    document_id=res["document_id"],
                    filename=res["title"], # Mapeamos title a filename
                    content_snippet=res["content_snippet"],
                    similarity_score=res["similarity_score"]
                ) for res in results
            ]
            
            Logger.add_to_log("info", f"AuditOrchestrator: Se encontraron {len(formatted_results)} resultados relevantes.")
            return formatted_results

        except Exception as e:
            Logger.add_to_log("error", f"Error en orquestador de búsqueda: {e}")
            # Elevamos el error para que el router lo maneje o retorne 500
            raise e
        
    async def answer_question(self, question: str):
        # 1. Guardrails Input (Validar que no sea una pregunta maliciosa)
        # TODO: Implementar validación de entrada
        
        # 2. Retrieval (Búsqueda de contexto)
        # Reutilizamos el método de búsqueda que acabamos de crear arriba
        context_docs = await self.perform_search(question, k=3)
        
        # 3. RAG Pipeline (Generación de respuesta)
        # Aquí llamaríamos al LLM pasándole 'question' y 'context_docs'
        # TODO: Implementar llamada a LLM
        
        # 4. Guardrails Output (Validar la respuesta del bot)
        # TODO: Implementar validación de salida
        
        return {
            "status": "work_in_progress", 
            "context_found": len(context_docs)
        }