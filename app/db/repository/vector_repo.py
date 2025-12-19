import os
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from app.core.logger import Logger
# Importamos tu servicio de embeddings (tal como lo tienes en tu archivo original)
from app.services.external.embedding_service import embedding_service

# Adaptador: Simplemente conecta ChromaDB con el servicio de embeddings.
class ChromaEmbeddingAdapter(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return embedding_service.generate_embeddings(input)

# Clase Repositorio
class VectorRepository:
    def __init__(self):
        # Definimos dónde guardar los datos para que no se borren al reiniciar
        self.persist_directory = "data/vector_store"
        os.makedirs(self.persist_directory, exist_ok=True)

        try:
            # Conectamos a la base de datos en disco
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Preparamos la función de embeddings
            self.embedding_fn = ChromaEmbeddingAdapter()

            # Obtenemos o creamos la colección
            self.collection = self.client.get_or_create_collection(
                name="iso_documents",
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"} # Usamos coseno para mejor precisión en texto
            )
            
            Logger.add_to_log("info", f"Base de datos vectorial lista en: {self.persist_directory}")

        except Exception as e:
            Logger.add_to_log("critical", f"Error conectando a ChromaDB: {e}")
            raise e

    # Método para guardar chunks
    def add_chunks(self, chunks_text: list, metadatas: list, ids: list):
        if not chunks_text:
            return
        
        try:
            # Usamos 'upsert' en lugar de 'add': 'add' falla si el ID ya existe. 'upsert' actualiza si existe o crea si no.
            self.collection.upsert(
                documents=chunks_text,
                metadatas=metadatas,
                ids=ids
            )
            Logger.add_to_log("info", f"Se guardaron {len(chunks_text)} fragmentos.")
            
        except Exception as e:
            Logger.add_to_log("error", f"Error guardando en vector store: {e}")
            raise e

    # Método para buscar
    def search_similarity(self, query: str, k: int = 3) -> list:
        Logger.add_to_log("info", f"Buscando: '{query}'")
        
        try:
            # Chroma hace el trabajo pesado: convierte query a vector y busca
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )

            # Chroma devuelve listas de listas
            formatted_results = []
            
            # Verificamos si encontramos algo
            if results['ids'] and results['ids'][0]:
                # Extraemos las listas internas (la posición 0)
                found_ids = results['ids'][0]
                found_metas = results['metadatas'][0]
                found_docs = results['documents'][0]
                found_dist = results['distances'][0] if results['distances'] else [0]*len(found_ids)

                # Recorremos los resultados para darles un formato bonito
                for i in range(len(found_ids)):
                    # Calculamos el score
                    score = round(1 / (1 + found_dist[i]), 4)
                    
                    item = {
                        "document_id": found_ids[i],
                        "title": found_metas[i].get("filename", "Desconocido"),
                        "content_snippet": found_docs[i],
                        "similarity_score": score,
                        "metadata": found_metas[i]
                    }
                    formatted_results.append(item)
            
            return formatted_results

        except Exception as e:
            Logger.add_to_log("error", f"Error buscando similitud: {e}")
            return []

    # Método extra para limpieza (Borrar documentos)
    def delete_by_doc_id(self, doc_id: str):
        try:
            # Borra todos los vectores donde "document_id" coincida
            self.collection.delete(where={"document_id": doc_id})
            Logger.add_to_log("info", f"Vectores borrados para documento: {doc_id}")
        except Exception as e:
            Logger.add_to_log("error", f"Error borrando vectores: {e}")

# Instanciamos globalmente
vector_repo = VectorRepository()