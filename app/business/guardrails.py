import json
from typing import Tuple
from app.core.logger import Logger
from app.core.constants import systemsPrompts
from app.services.external.llm_factory import LLMFactory

# Clase encargada de la seguridad semántica usando LLM-as-a-Judge.
class Guardrails:
    def __init__(self):
        # En lugar de crear el cliente aquí, se lo pedimos a la Factory
        self.client = LLMFactory.create_cohere_client_v2()
        
        self.model_name = "command-r7b-12-2024" # Modelo para validación (rápido)

    def _parse_json_response(self, raw_text: str) -> dict:
        try:
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip() # Limpiamos bloques de código markdown si el LLM los agrega
            print(cleaned_text)
            return json.loads(cleaned_text) # Convertimos el string a diccionario Python

        except json.JSONDecodeError:
            Logger.add_to_log("error", f"Guardrails: Error parseando JSON: {raw_text}")
            
            # Si falla, retornamos un bloqueo por seguridad
            return {
                "publicable": "No", 
                "analisis": "Error de formato JSON en Guardrail"
            }

    def _ask_cohere_judge(self, system_prompt: str, user_text: str) -> dict:
        try:
            # Usamos self.client que vino de la Factory
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                temperature=0,
                seed=123
            )
            print("Validando respuesta:",response)
            
            # Validación defensiva por si la respuesta viene vacía
            if not response.message or not response.message.content:
                 raise ValueError("Respuesta vacía de Cohere")

            raw_content = response.message.content[0].text
            return self._parse_json_response(raw_content)

        except Exception as e:
            Logger.add_to_log("error", f"Guardrails: Fallo con error de conexión de IA: {e}")
            # Fail Safe: Bloqueo por defecto
            return {"publicable": "No", "analisis": "Error de conexión IA"}

    # Método para validar la entrada al RAG    
    def validate_input(self, question: str) -> Tuple[bool, str]:
        Logger.add_to_log("info", "Guardrails: Validando entrada...")
        
        # Obtenemos el veredicto del LLM
        result = self._ask_cohere_judge(systemsPrompts.system_prompt_guardrail_input, question)
        print(f"El modelo respondión esto: {result}")
        
        # Extraemos las variables del diccionario
        es_publicable = result.get("publicable", "No") # Si no viene la clave que tome "No"
        razon_analisis = result.get("analisis", "Bloqueo preventivo sin análisis")
        
        # Estructura de decisión clara
        if es_publicable == "Si":
            return True, ""
            
        else:
            Logger.add_to_log("warning", f"Se ha bloqueado la entrada de una pregunta. Razón: {razon_analisis}")
            # Retornamos False y la razón del bloqueo para mostrársela al usuario.
            return False, razon_analisis

    # Método para validar la salida del RAG
    def validate_output(self, answer: str) -> Tuple[bool, str]:
        # (Mismo código que te pasé antes)
        Logger.add_to_log("info", "Guardrails: Validando salida...")
        result = self._ask_cohere_judge(systemsPrompts.system_prompt_guardrail_output, answer)
        
        es_publicable = result.get("publicable", "No")
        razon_analisis = result.get("analisis", "Bloqueo preventivo")

        # Estructura de decisión clara
        if es_publicable == "Si":
            return True, ""
            
        else:
            Logger.add_to_log("warning", "Se ha bloqueado la salida de una respuesta. Razón: {razon_analisis}")
            # Retornamos False y la razón del bloqueo para mostrársela al usuario.
            return False, razon_analisis