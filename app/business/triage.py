import json
from app.core.logger import Logger
from app.core.constants import systemsPrompts
from app.services.external.llm_factory import LLMFactory

class TriageService:
    def __init__(self):
        self.client = LLMFactory.create_cohere_client_v2()
        self.model = "command-r-08-2024" # Modelo más rápido y barato para esto

    def predict_intent(self, text: str) -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": systemsPrompts.system_prompt_triage},
                    {"role": "user", "content": text}
                ],
                temperature=0,
                seed=123
            )
            raw_content = response.message.content[0].text

            # Limpieza básica del JSON
            clean_json = raw_content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            intent = data.get("categoria", "ISO_QUERY") # Default a ISO si falla
            Logger.add_to_log("info", f"Triage: Intención detectada -> {intent}")
            return intent

        except Exception as e:
            Logger.add_to_log("error", f"Error en Triage: {e}")
            return "ISO_QUERY" # Fail-open: Ante la duda, intentamos buscar.