# Archivo para orquestar toda la lógica de negocios
from fastapi import HTTPException
from app.core.logger import Logger


class AuditOrchestrator:
    def __init__(self):
        # cargamos los otros business
        self.rag_pipeline = RagPipeline()
        self.guardrails = Guardrails()

    async def answer_question(self, question: str):
        # 1. Guardrails Input
        # 2. Triage
        # 3. RAG Pipeline
        # 4. Guardrails Output
        pass