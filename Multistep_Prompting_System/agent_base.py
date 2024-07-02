import os
import json
import logging
from typing import Dict, Any, Optional
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self):
        self.prompts = None
        self.client = None
        self.default_model = "claude-3-sonnet-20240229"

    def load_prompts(self, file_path: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Próba otwarcia pliku: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"Błąd: Plik {file_path} nie istnieje.")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                logger.info(f"Plik {file_path} otwarty pomyślnie")
                data = json.load(file)
                logger.info(f"JSON załadowany pomyślnie z {file_path}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Błąd dekodowania JSON: {str(e)}")
        except PermissionError:
            logger.error(f"Brak uprawnień do odczytu pliku: {file_path}")
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas ładowania pliku JSON: {str(e)}")
        return None

    def initialize_anthropic_client(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Brak klucza API Anthropic w zmiennych środowiskowych")
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("Klucz API Anthropic załadowany pomyślnie")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, model: str, original_query: str) -> str:
        try:
            logger.info(f"Wysyłanie zapytania do modelu: {model}")
            response = self.client.messages.create(
                model=model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=30
            )
            logger.info("Odpowiedź otrzymana pomyślnie")
            
            logger.info(f"Pełna odpowiedź API: {response}")

            if not response or 'content' not in response:
                raise ValueError("Otrzymano pustą odpowiedź od API")

            if not response['content']:
                raise ValueError("Otrzymano pustą odpowiedź od API")

            if not response['content'][0].get('text'):
                raise ValueError("Otrzymano pustą odpowiedź od API")

            answer = response['content'][0]['text']
            return answer
        except anthropic.APIError as e:
            logger.error(f"Błąd API Anthropic: {e}")
            if "not_found_error" in str(e):
                logger.warning(f"Model {model} nie został znaleziony. Próba użycia modelu domyślnego.")
                if model != self.default_model:
                    return self.generate_response(prompt, self.default_model, original_query)
            raise
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd w generate_response: {e}", exc_info=True)
            raise

    def change_default_model(self, new_model: str):
        self.default_model = new_model
        logger.info(f"Zmieniono domyślny model na: {new_model}")

    def process_query(self, query: str, dzial_info: Dict[str, Any]) -> str:
        raise NotImplementedError("Ta metoda powinna być zaimplementowana w klasach pochodnych")