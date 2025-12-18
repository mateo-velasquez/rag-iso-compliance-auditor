# Archivo para orquestar toda la lógica de negocios

from fastapi import UploadFile, HTTPException
from app.services.external.pdf_processor import PDFProcessor
from app.db.repository.document_repo import DocumentRepository
from app.db.models.documents import UserDocumentDB
from app.core.logger import Logger
from app.schemas.audit import (
    DocumentUploadRequest,
    DocumentUploadResponse
)

class AuditOrchestrator:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.doc_repo = DocumentRepository()

    async def answer_question(self, question: str):
        # 1. Guardrails Input
        # 2. Triage
        # 3. RAG Pipeline
        # 4. Guardrails Output
        pass