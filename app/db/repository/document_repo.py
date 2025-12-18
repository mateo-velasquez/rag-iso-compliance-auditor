from app.db.mongo_db import mongo_manager
from app.db.models.documents import UserDocumentDB 
from app.core.logger import Logger
from datetime import datetime, timezone

# Clase que guarde nuestros datos (sin subir el archivo) en MongoDB
class DocumentRepository:
    def __init__(self):
        self.db = mongo_manager.db
        self.collection = self.db["documents"]

    # Busca si ya existe un archivo activo con ese hash
    async def create(self, document: UserDocumentDB):
        doc_dict = document.model_dump(by_alias=True)
        result = await self.collection.insert_one(doc_dict)
        Logger.add_to_log("debug", f"Documento insertado en Mongo ID: {result.inserted_id}")
        return document
    
    # Busca si ya existe un archivo activo con ese hash
    async def get_by_hash(self, file_hash: str):
        return await self.collection.find_one({"file_hash": file_hash, "is_active": True})
    
    # Busca un documento por su ID
    async def get_by_id(self, id: str):
        return await self.collection.find_one({
            "_id": id, 
            "is_active": True
        })

# Actualiza campos específicos del documento
    async def update(self, id: str, update_data: dict):
        # Siempre actualizamos la fecha de modificación
        update_data["update_date"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"_id": id},
            {"$set": update_data}
        )
        Logger.add_to_log("debug", f"Documento insertado en CromaDB ID: {result.upserted_id}")
        return result.modified_count > 0

    # Método auxiliar para cambiar estado (PATCH)
    async def update_status(self, id: str, status: str, error_msg: str = None):
        data = {
            "status": status,
            "update_date": datetime.now(timezone.utc)
        }
        if error_msg:
            data["error_msg"] = error_msg

        await self.collection.update_one(
            {"_id": id},
            {"$set": data}
        )
        Logger.add_to_log("info", f"Estado del documento {id} actualizado a: {status}")

    # Borrado lógico: No elimina el registro, solo lo marca como inactivo.
    async def delete_by_id(self, id: str):
        result = await self.collection.update_one(
            {"_id": id},
            {
                "$set": {
                    "is_active": False,
                    "deleted_date": datetime.now(timezone.utc),
                    "update_date": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            Logger.add_to_log("info", f"Documento {id} eliminado lógicamente (Soft Delete).")
            return True
        else:
            Logger.add_to_log("warning", f"Intento de borrar documento {id} fallido o no encontrado.")
            return False