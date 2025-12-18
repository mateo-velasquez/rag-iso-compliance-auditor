
from fastapi import UploadFile, HTTPException
from app.services.external.pdf_processor import PDFProcessor
from app.db.repository.document_repo import DocumentRepository
from app.core.logger import Logger
from app.db.models.documents import UserDocumentDB
from app.schemas.audit import DocumentUploadResponse

class DocumentManager:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.doc_repo = DocumentRepository()

    # Cargar archivo
    async def handle_upload(self, file: UploadFile) -> DocumentUploadResponse:
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

    # --- READ ---
    async def get_all_documents(self):
        # Llama al repo para listar todos (puedes agregar filtros)
        docs = await self.doc_repo.get_all_active() 
        return docs

    async def get_document_by_id(self, doc_id: str):
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return doc

    # --- DELETE (Soft Delete) ---
    async def delete_document(self, doc_id: str):
        # 1. Verificar si existe
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        # 2. Borrado Lógico en BD
        success = await self.doc_repo.delete_by_id(doc_id)
        
        # Opcional: ¿Borrar el archivo físico o dejarlo por auditoría?
        # Generalmente en auditoría NO se borra lo físico, solo se desactiva en BD.
        
        return {"message": "Documento eliminado correctamente", "id": doc_id}