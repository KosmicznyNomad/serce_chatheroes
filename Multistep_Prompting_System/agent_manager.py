import os
import json
import logging
from typing import Dict, Any, Optional, List
from agent_base import BaseAgent
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentManager(BaseAgent):
    def __init__(self):
        super().__init__()
        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'knowledge_base.json'))
        logger.info(f"Ścieżka do pliku JSON: {json_path}")
        self.prompts = self.load_prompts(json_path)
        if self.prompts is None or not self.prompts.get('dzialy'):
            raise ValueError("Nie udało się załadować poprawnych danych z pliku JSON")
        
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Brak klucza API Anthropic w zmiennych środowiskowych")
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("Klucz API Anthropic załadowany pomyślnie")
        self.default_model = "claude-3-sonnet-20240229"  # Dodano definicję default_model

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
                logger.info(f"Zawartość JSON z {file_path}: {json.dumps(data, indent=2)}")
                
                if not self.validate_json_structure(data):
                    return None
                
                logger.info(f"Załadowano {len(data.get('dzialy', []))} działów z {file_path}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Błąd dekodowania JSON: {str(e)}")
        except PermissionError:
            logger.error(f"Brak uprawnień do odczytu pliku: {file_path}")
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas ładowania pliku JSON: {str(e)}")
        return None

    def validate_json_structure(self, data: Dict[str, Any]) -> bool:
        if not data:
            logger.error("Plik JSON jest pusty")
            return False
        
        if "dzialy" not in data:
            logger.error("Brak klucza 'dzialy' w pliku JSON")
            return False
        
        if not isinstance(data["dzialy"], list):
            logger.error("Klucz 'dzialy' nie jest listą")
            return False
        
        if not data["dzialy"]:
            logger.warning("Lista działów jest pusta")
            return False
        
        for dzial in data["dzialy"]:
            if not self.validate_dzial_structure(dzial):
                return False
        
        return True

    def validate_dzial_structure(self, dzial: Dict[str, Any]) -> bool:
        required_keys = ["nazwa", "opis", "tematy"]
        for key in required_keys:
            if key not in dzial:
                logger.error(f"Brak wymaganego klucza '{key}' w dziale")
                return False
        
        if not isinstance(dzial["tematy"], list):
            logger.error("Klucz 'tematy' nie jest listą")
            return False
        
        for temat in dzial["tematy"]:
            if not self.validate_temat_structure(temat):
                return False
        
        return True

    def validate_temat_structure(self, temat: Dict[str, Any]) -> bool:
        required_keys = ["nazwa", "wymagania", "niewymagane"]
        for key in required_keys:
            if key not in temat:
                logger.error(f"Brak wymaganego klucza '{key}' w temacie")
                return False
        
        if not isinstance(temat["wymagania"], list) or not isinstance(temat["niewymagane"], list):
            logger.error("Klucze 'wymagania' lub 'niewymagane' nie są listami")
            return False
        
        return True

    def process_query(self, query: str, dzial_info: Dict[str, Any]) -> str:
        return self.multistep_prompting(query, dzial_info)

    def multistep_prompting(self, query: str, dzial_info: Dict[str, Any]) -> str:
        try:
            if not dzial_info:
                logger.warning("Brak informacji o dziale. Nie można przetworzyć zapytania.")
                return "Przepraszam, ale nie mam wystarczających informacji, aby odpowiedzieć na Twoje pytanie."

            # Pierwszy krok: uzyskanie odpowiedzi z bazy wiedzy JSON
            initial_response = self._process_query(query, dzial_info, step="initial")
            if not initial_response:
                return "Nie udało się przetworzyć zapytania."

            # Drugi krok: stylizowanie odpowiedzi na Mickiewicza
            followup_query = f"Na podstawie odpowiedzi: {initial_response}, przetwórz odpowiedź na pytanie: {query}"
            followup_response = self._process_query(followup_query, dzial_info, step="followup", initial_response=initial_response)

            # Upewnij się, że followup_response nie jest puste
            if not followup_response:
                logger.error("Otrzymano pustą odpowiedź w drugim kroku promptowania")
                return "Przepraszam, wystąpił błąd podczas przetwarzania Twojego pytania."

            final_response = f"Pytanie ucznia: {query}\n\nOdpowiedź: {followup_response}"
            return final_response
        except RetryError as e:
            logger.error(f"Wystąpił błąd RetryError: {str(e)}")
            return f"Przepraszam, wystąpił błąd podczas przetwarzania Twojego pytania. Proszę spróbować ponownie później."
        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd: {str(e)}", exc_info=True)
            return f"Przepraszam, wystąpił nieoczekiwany błąd podczas przetwarzania Twojego pytania: {str(e)}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _process_query(self, query: str, dzial_info: Dict[str, Any], step: str, initial_response: str = "") -> str:
        try:
            if not dzial_info:
                logger.error("Brak informacji o dziale")
                return "Przepraszam, ale nie mam dostępu do informacji o dziale. Nie mogę odpowiedzieć na Twoje pytanie."

            if step == "initial":
                # Pierwszy krok: odpowiedź na podstawie bazy wiedzy
                prompt = f"""
                Jako nauczyciel z wieloletnim doświadczeniem, wypisz kluczowe informacje z programu szkolnego, które są wymagane do omówienia tego działu. Uwzględnij ciekawostkę oraz kluczowe dane. 

                Dział: {dzial_info['nazwa']}
                Opis działu: {dzial_info['opis']}
                Tematy:
                {self._format_topics(dzial_info.get('tematy', []))}

                Pytanie ucznia: {query}

                Odpowiedź:
                """
            elif step == "followup":
                # Drugi krok: stylizowanie odpowiedzi na Mickiewicza
                prompt = f"""
                Zamień odpowiedź z pierwszego kroku w zrozumiałą odpowiedź na pytanie ucznia. Wykorzystaj techniki prezentowania informacji najlepszych nauczycieli, którzy tłumaczą materiał za pomocą zrozumiałych analogii. Pisz w pierwszej osobie jako Adam Mickiewicz, poeta, który korzysta z współczesnego słownictwa przystępnego dla dyslektyków. Pisz tekst w formie pierwszoosobowej. Skorzystaj miejscami z humoru. 
        
                Odpowiedź z pierwszego kroku: {initial_response}
                Pytanie ucznia: {query}

                Twoja odpowiedź:
                """
            else:
                logger.error(f"Nieznany krok: {step}")
                return "Przepraszam, wystąpił błąd w przetwarzaniu zapytania."

            response = self.generate_response(prompt, model=self.default_model, original_query=query)
            
            # Dodaj logowanie odpowiedzi
            logger.info(f"Odpowiedź dla kroku {step}: {response}")
            
            return response
        except KeyError as e:
            logger.error(f"Wystąpił błąd KeyError w _process_query: {str(e)}", exc_info=True)
            return "Przepraszam, wystąpił błąd w przetwarzaniu danych. Proszę spróbować ponownie."
        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd w _process_query: {str(e)}", exc_info=True)
            return "Przepraszam, wystąpił nieoczekiwany błąd. Proszę spróbować ponownie później."

    def _format_topics(self, topics: List[Dict[str, Any]]) -> str:
        formatted_topics = ""
        for topic in topics:
            formatted_topics += f"- {topic['nazwa']}\n"
            formatted_topics += "  Wymagania:\n"
            for req in topic.get('wymagania', []):
                formatted_topics += f"    * {req}\n"
            formatted_topics += "  Niewymagane:\n"
            for non_req in topic.get('niewymagane', []):
                formatted_topics += f"    * {non_req}\n"
        return formatted_topics

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
                timeout=30  # Dodano timeout
            )
            logger.info("Odpowiedź otrzymana pomyślnie")
            
            # Logowanie pełnej odpowiedzi
            logger.info(f"Pełna odpowiedź API: {response}")

            if not response:
                logger.error("Otrzymano pustą odpowiedź od API")
                return "Przepraszam, wystąpił błąd podczas generowania odpowiedzi."

            if not isinstance(response, anthropic.types.message.Message):
                logger.error(f"Nieoczekiwany format odpowiedzi: {type(response)}")
                return "Przepraszam, wystąpił błąd podczas przetwarzania odpowiedzi."

            if not response.content:
                logger.error("Brak zawartości w odpowiedzi API")
                return "Przepraszam, otrzymano pustą odpowiedź."

            if not isinstance(response.content, list) or len(response.content) == 0:
                logger.error(f"Nieoczekiwana struktura 'content': {response.content}")
                return "Przepraszam, wystąpił błąd w formacie odpowiedzi."

            if not hasattr(response.content[0], 'text'):
                logger.error("Brak atrybutu 'text' w pierwszym elemencie 'content'")
                return "Przepraszam, nie udało się odczytać odpowiedzi."

            answer = response.content[0].text
            if not answer:
                logger.error("Otrzymano pustą odpowiedź tekstową")
                return "Przepraszam, otrzymano pustą odpowiedź tekstową."

            return answer
        except anthropic.APIError as e:
            logger.error(f"Błąd API Anthropic: {e}")
            if "not_found_error" in str(e):
                logger.warning(f"Model {model} nie został znaleziony. Próba użycia modelu domyślnego.")
                if model != self.default_model:
                    return self.generate_response(prompt, self.default_model, original_query)
            return f"Przepraszam, wystąpił błąd API: {str(e)}"
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd w generate_response: {e}", exc_info=True)
            return f"Przepraszam, wystąpił nieoczekiwany błąd: {str(e)}"

    def change_default_model(self, new_model: str):
        self.default_model = new_model
        logger.info(f"Zmieniono domyślny model na: {new_model}")