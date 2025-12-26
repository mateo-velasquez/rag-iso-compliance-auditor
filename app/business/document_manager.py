from typing import List
from fastapi import UploadFile, HTTPException
from app.services.external.pdf_processor import PDFProcessor
from app.db.repository.document_repo import DocumentRepository
from app.db.repository.vector_repo import VectorRepository
from app.core.logger import Logger
from app.db.models.documents import UserDocumentDB
from app.schemas.documents import DocumentResponse, DocumentResponseComplete

class DocumentManager:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.doc_repo = DocumentRepository()
        self.vector_repo = VectorRepository()

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
        
    # Método para procesar vectorialmente un archivo
    async def _process_vectors(self, file_path: str, doc_id: str, filename: str):
        # Extraemos el texto del PDF
        Logger.add_to_log("info", f"Comenzando el procesamiento vectorial para el archivo con ID: {doc_id}")
        full_text = self.pdf_processor.extract_text(file_path)
        
        if not full_text:
            Logger.add_to_log("warning", f"El archivo {doc_id} no tiene texto extraíble.")
            return
        
        # Aca comienzo a hacer la división en chunks, así que inicializo algunas variables:
        CHUNK_SIZE = 1000
        OVERLAP = 100
        chunks = []
        ids = []
        metadatas = []
        start = 0
        text_len = len(full_text)

        # Ventana Deslizante: Cortamos y avanzamos, pero retrocedemos un poco (overlap)
        while start < text_len:
            end = min(start + CHUNK_SIZE, text_len) # Calculamos el final del corte actual
            
            chunk_text = full_text[start:end] # Extraemos el fragmento de texto
            
            chunks.append(chunk_text) # Guardamos los datos en las listas
            
            # Generamos un ID único para cada pedacito (ej: "doc123_0", "doc123_1")
            ids.append(f"{doc_id}_{len(chunks)}")
            
            # Guardamos metadata para saber a qué archivo pertenece este pedazo
            metadatas.append({
                "document_id": doc_id, 
                "filename": filename,
                "chunk_index": len(chunks)
            })

            # Condición de salida para evitar bucles infinitos al final del texto
            if end == text_len:
                break
            
            # Avanzamos el cursor: Tamaño del chunk menos el overlap (Si tamaño=500 y overlap=50, avanzamos 450 caracteres)
            start += CHUNK_SIZE - OVERLAP
            
        Logger.add_to_log("info", f"Texto dividido en {len(chunks)} fragmentos de {CHUNK_SIZE} chars (overlap {OVERLAP}).")

        # Guardamos en el repositorio
        self.vector_repo.add_chunks(chunks, metadatas, ids)

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
            
            # Al reactivar, nos aseguramos que esté en los vectores
            await self._process_vectors(file_path, doc_id, file.filename)

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
        doc_id = new_doc.id

        # Procesamiento vectorial
        try:
            await self._process_vectors(file_path, doc_id, file.filename)
        except Exception as e:
            # Rollback: Si falla vectorizar, borramos de Mongo para no dejar datos corruptos
            await self.doc_repo.delete_by_id(doc_id)
            Logger.add_to_log("error", f"Fallo vectorización. Rollback ejecutado: {e}")
            raise HTTPException(status_code=500, detail="Error procesando el contenido del archivo.")

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

        await self.doc_repo.delete_by_id(doc_id) # Lo borra de mongo (lógico)

        self.vector_repo.delete_by_doc_id(doc_id) # Lo borra de la base vectorial

        Logger.add_to_log("info", f"Borrado lógico exitoso: {doc_id}")
        
        return DocumentResponse(
            message="Documento borrado correctamente",
            document_id=doc_id
        )