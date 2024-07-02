import anthropic
import os
from dotenv import load_dotenv
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self):
<<<<<<< HEAD
        # Załaduj zmienne środowiskowe z pliku .env
        load_dotenv()
        
        # Pobierz klucz API ze zmiennych środowiskowych
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Klucz API Anthropic nie został znaleziony w zmiennych środowiskowych.")
        
        # Inicjalizacja klienta Anthropic
        self.client = anthropic.Client(api_key=api_key)
        
        # Domyślny model
        self.default_model = "claude-2.1"  # Zmieniono na bardziej stabilny model
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, model: str = None) -> str:
        model = model or self.default_model
=======
        self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_response(self, prompt: str, model: str = "claude-3-5-sonnet-20240620") -> str:
>>>>>>> 3677e640d95ba8db0924798d0c693a54531e515c
        try:
            logger.info(f"Wysyłanie zapytania do modelu: {model}")
            response = self.client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            logger.info("Odpowiedź otrzymana pomyślnie")
            return response.content[0].text
        except anthropic.APIError as e:
            logger.error(f"Błąd API Anthropic: {e}")
            if "not_found_error" in str(e):
                logger.warning(f"Model {model} nie został znaleziony. Próba użycia modelu domyślnego.")
                if model != self.default_model:
                    return self.generate_response(prompt, self.default_model)
            raise  # Ponowne rzucenie wyjątku, aby retry mógł go obsłużyć
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd: {e}")
            raise

    def change_default_model(self, new_model: str):
        """Zmienia domyślny model używany przez agenta."""
        self.default_model = new_model
        logger.info(f"Zmieniono domyślny model na: {new_model}")