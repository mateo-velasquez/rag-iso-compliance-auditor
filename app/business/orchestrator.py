# Archivo para orquestar toda la lógica de negocios
from typing import List
from app.core.logger import Logger
from app.db.repository.vector_repo import vector_repo
from app.schemas.audit import SearchResult, AskResponse
from app.business.guardrails import Guardrails
from app.business.triage import TriageService
from app.business.rag_pipeline import RagPipeline

# Clase orquestador
class AuditOrchestrator:
    def __init__(self):
        # cargamos los otros business
        self.rag_pipeline = RagPipeline()
        self.guardrails = Guardrails()
        self.triage = TriageService()
        self.vector_db = vector_repo

    async def answer_question(self, question: str) -> AskResponse:
        # Primero valido la pregunta antes de ingresar en el RAG
        is_valid_input, rejection_reason = self.guardrails.validate_input(question)
        if not is_valid_input:
            Logger.add_to_log("warning", f"Orchestrator: Input rechazada: {rejection_reason}")
            # Retornamos estructura válida pero indicando que no está fundamentada (grounded=False)
            return AskResponse(
                answer="Lo siento pero no puedo responderte esa pregunta",
                context_used=None,
                similarity_score=None,
                grounded=False
            )
        
        # Segundo llamo al Triage para ver la Intención:
        intent = self.triage.predict_intent(question)
        Logger.add_to_log("info", f"Orchestrator: Intención detectada -> {intent}")

        # Caso: pregunta fuera de tópico
        if intent == "OFF_TOPIC":
            return AskResponse(
                answer="Lo siento, pero esa pregunta se escapa de mis funciones, por favor introduce una pregunta válida",
                grounded=False, # No usa contexto, es hardcoded
                context_used=None,
                similarity_score=0.0
            )
        
        # Caso: saludo
        elif intent == "GREETING_HI":
            return AskResponse(
                answer="¡Hola! Soy Cleo, tu asistente de auditoría ISO. ¿En qué puedo ayudarte hoy?",
                grounded=False, # No usa contexto, es hardcoded
                context_used=None,
                similarity_score=0.0
            )
        
        # Caso: Despedida
        elif intent == "GREETING_BYE":
            return AskResponse(
                answer="¡Hasta Luego! Fue un verdadero placer ayudarte ¡Vuelve cuando quieras!",
                grounded=False, # No usa contexto, es hardcoded
                context_used=None,
                similarity_score=0.0
            )

        elif intent == "ISO_QUERY":
            # DELEGACIÓN: Llamamos al pipeline que se encarga de buscar y generar
            generated_answer, context_docs, top_score = await self.rag_pipeline.run(question)
            
            # Caso: El pipeline no encontró documentos (retornó lista vacía)
            if not context_docs:
                Logger.add_to_log("error", f"Orchestrator: Rag_pipeline fallado")
                return AskResponse(
                    answer="¡Lo siento! No encontré información para tu pregunta",
                    grounded=False,
                    context_used=None,
                    similarity_score=0.0
                )
            
            # Recuperamos el snippet del mejor documento para mostrarlo como evidencia
            best_doc_snippet = context_docs[0]['content_snippet']
            
            # GUARDRAILS OUTPUT (Solo se aplica si generamos contenido con IA)
            is_safe_output, output_reason = self.guardrails.validate_output(generated_answer)
            
            if not is_safe_output:
                Logger.add_to_log("warning", f"Orchestrator: Output rechazada: {output_reason}")
                return AskResponse(
                    answer="Lo siento, la respuesta generada no cumple con las políticas de seguridad.",
                    context_used=None, 
                    similarity_score=None,
                    grounded=False
                )

            # ÉXITO: Retornamos la respuesta generada y validada
            return AskResponse(
                answer=generated_answer,
                context_used=best_doc_snippet,
                similarity_score=top_score,
                grounded=True
            )

        # CASO E: FALLBACK (Si el Triage devuelve algo inesperado)
        else:
            return AskResponse(
                answer="No he podido entender tu intención. Por favor, reformula la pregunta.",
                grounded=False,
                context_used=None,
                similarity_score=0.0
            )

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
        