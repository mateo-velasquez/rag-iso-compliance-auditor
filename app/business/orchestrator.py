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

    # Método para cargar PDFs
    async def handle_upload(self, file: UploadFile) -> dict:
        Logger.add_to_log("info", f"Iniciando upload para: {file.filename}")
        file_path, file_hash = await self.pdf_processor.save_file(file) # Guardamos el documento físico y obtener Hash

        # Verificamos duplicados en BD (Deduplicación)
        existing_doc = await self.doc_repo.get_by_hash(file_hash)
        if existing_doc:
            Logger.add_to_log("info", "Documento duplicado detectado. Retornando existente.")
            # Convertimos el objeto de mongo a string para retornarlo
            return DocumentUploadResponse(
                message="El archivo ya existe en la base de datos.",
                document_id=str(existing_doc["_id"]) # OJO: 'document_id', no 'id'
            )

        # Creamos la Metadata
        new_doc = UserDocumentDB(
            filename=file.filename,
            file_path=file_path,
            file_hash=file_hash
        )

        # Guardamos en Mongo
        await self.doc_repo.create(new_doc)

        # Asignamos el response
        response = DocumentUploadResponse(
            message="Documento subido correctamente",
            document_id=new_doc.id
        )
        return response
    

    # Método para borrar (lógicamente) un PDF
    #async def handl