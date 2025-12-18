import os
import hashlib
from fastapi import UploadFile
from app.core.logger import Logger

class PDFProcessor:
    UPLOAD_DIR = "data/files"

    def __init__(self):
        # Aseguramos que el directorio exista
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    # Función que guarda archivos y retorna su ruta y su hash
    async def save_file(self, file: UploadFile) -> tuple[str, str]:
        try:
            # Leemos el contenido para hashearlo
            content = await file.read()
            sha256_hash = hashlib.sha256(content).hexdigest()
            
            # Reseteamos el cursor del archivo (importante para leerlo de nuevo)
            await file.seek(0)
            
            # Definimos la ruta (Usamos el hash en el nombre para evitar colisiones de nombres iguales)
            file_path = os.path.join(self.UPLOAD_DIR, f"{sha256_hash}_{file.filename}")
            
            # Guardamos en disco (si no existe ya)
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(content)
                Logger.add_to_log("info", f"Archivo guardado en disco: {file_path}")
            else:
                Logger.add_to_log("info", f"Archivo físico ya existía (Deduplicación): {file_path}")

            return file_path, sha256_hash

        except Exception as e:
            Logger.add_to_log("error", f"Error procesando PDF: {e}")
            raise e