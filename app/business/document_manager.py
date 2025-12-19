from typing import List
from fastapi import UploadFile, HTTPException
from app.services.external.pdf_processor import PDFProcessor
from app.db.repository.document_repo import DocumentRepository
from app.core.logger import Logger
from app.db.models.documents import UserDocumentDB
from app.schemas.documents import DocumentResponse, DocumentResponseComplete

class DocumentManager:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.doc_repo = DocumentRepository()

    # Método que transforma los formatos
    def _map_to_response_complete(self, doc_data: dict) -> DocumentResponseComplete:
        try:
            return DocumentResponseComplete(
                id=str(doc_data["_id"]),  # Conversión crítica
                filename=doc_data["filename"],
                file_path=doc_data["file_path"],
                file_hash=doc_data["file_hash"],
                upload_date=doc_data["upload_date"],
                update_date=doc_data["update_date"],
                iso_version_target=doc_data.get("iso_version_target", "2022"), 
                doc_type=doc_data.get("doc_type", "other"),
                status=doc_data.get("status", "pending")
            )
        except Exception as e:
            Logger.add_to_log("error", f"Error mapeando documento {doc_data.get('_id')}: {e}")
            raise HTTPException(status_code=500, detail="Error interno procesando datos del documento")

    # Permite cargar un archivo PDF
    async def handle_upload(self, file: UploadFile) -> DocumentResponse:
        Logger.add_to_log("info", f"Iniciando upload para: {file.filename}")
        file_path, file_hash = await self.pdf_processor.save_file(file)

        # Si ya existe un archivo con sus características y está activo que lo retorne
        existing_doc = await self.doc_repo.get_by_hash(file_hash)
        if existing_doc:
            Logger.add_to_log("info", "Documento duplicado activo. Retornando existente.")
            return DocumentResponse(
                message="El archivo ya existe y está activo.",
                document_id=str(existing_doc["_id"])
            )

        # Si existe pero fue borrado que lo reactive
        deleted_doc = await self.doc_repo.get_deleted_by_hash(file_hash)
        if deleted_doc:
            doc_id = str(deleted_doc["_id"])
            Logger.add_to_log("info", f"Documento borrado encontrado ({doc_id}). Reactivando...")
            
            await self.doc_repo.reactivate(doc_id)
            
            return DocumentResponse(
                message="El archivo existía en papelera y ha sido restaurado.",
                document_id=doc_id
            )

        # que genere uno nuevo
        new_doc = UserDocumentDB(
            filename=file.filename,
            file_path=file_path,
            file_hash=file_hash
        )

        await self.doc_repo.create(new_doc)

        return DocumentResponse(
            message="Documento subido correctamente",
            document_id=new_doc.id
        )

    # Método para traer a todos los documentos
    async def get_all_documents(self) -> List[DocumentResponseComplete]:
        Logger.add_to_log("info", "Trayendo todos los documentos")
        
        docs_raw = await self.doc_repo.get_all_active()
        
        if not docs_raw:
            Logger.add_to_log("debug", "No se encontraron documentos activos.")
            return [] # Retornamos lista vacía en vez de 404

        # Convertimos cada diccionario al Schema usando el mapper
        response_list = [self._map_to_response_complete(doc) for doc in docs_raw]
        
        return response_list

    # Método que trae un documento por su id
    async def get_document_by_id(self, doc_id: str) -> DocumentResponseComplete:
        Logger.add_to_log("info", f"Iniciando get_document para el id: {doc_id}")
        
        doc_raw = await self.doc_repo.get_by_id(doc_id)
        
        if not doc_raw:
            Logger.add_to_log("warning", f"No se encontró el documento con id: {doc_id}")
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        # Retornamos el objeto mapeado
        return self._map_to_response_complete(doc_raw)

    # Método para hacer el borrado lógico
    async def delete_document(self, doc_id: str):
        Logger.add_to_log("info", f"Iniciando borrado lógico: {doc_id}")
        
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        await self.doc_repo.delete_by_id(doc_id)
        Logger.add_to_log("info", f"Borrado lógico exitoso: {doc_id}")
        
        return DocumentResponse(
            message="Documento borrado correctamente",
            document_id=doc_id
        )