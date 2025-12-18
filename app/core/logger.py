# Archivo para hacer el logger

import logging
import os
import traceback
import sys

class Logger:
    _logger = None  # Variable de clase para guardar la instancia única

    @classmethod
    def __get_logger(cls):
        # Configura el logger UNA sola vez. Si ya existe, lo devuelve.
        if cls._logger:
            return cls._logger

        # Configuración de Directorios (Evita error si no existe la carpeta)
        log_directory = "logs"
        log_filename = "app.log"
        
        if not os.path.exists(log_directory):
            try:
                os.makedirs(log_directory)
            except OSError as e:
                print(f"Error crítico creando directorio de logs: {e}")

        # Configuración del Logger Base
        logger = logging.getLogger("RAG-ISO-COMPLIANCE-AUDITOR") # Nombre fijo para identificar tu app
        logger.setLevel(logging.DEBUG)
        
        # Evitamos duplicar handlers si se llama varias veces por error
        if logger.hasHandlers():
            logger.handlers.clear()

        # Formato Estandarizado
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s', 
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Handler 1: Archivo
        try:
            log_path = os.path.join(log_directory, log_filename)
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"No se pudo configurar el log en archivo: {e}")

        # Handler 2: Consola (Para ver errores en tiempo real)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO) # En consola mostramos solo INFO para no saturar
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        cls._logger = logger
        return cls._logger
    
    @classmethod
    def add_to_log(cls, level: str, message: str):
        try:
            # Obtenemos la instancia
            logger = cls.__get_logger()
            
            # Normalizamos el nivel a minúsculas
            lvl = level.lower()

            if lvl == "critical":
                logger.critical(message)
            elif lvl == "debug":
                logger.debug(message)
            elif lvl == "error":
                logger.error(message)
            elif lvl == "info":
                logger.info(message)
            elif lvl == "warning" or lvl == "warm":
                logger.warning(message)
            else:
                logger.info(f"[NIVEL DESCONOCIDO: {level}] {message}")

        except Exception as ex:
            print(traceback.format_exc()) # traceback is not define
            print(ex)