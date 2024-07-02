import os
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def load_prompts(file_path: str) -> Dict[str, Any]:
    logging.info(f"Próba otwarcia pliku: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            logging.info("Plik otwarty pomyślnie")
            data = json.load(file)
            logging.info("JSON załadowany pomyślnie")
            logging.info(f"Struktura JSON: {json.dumps(data, indent=2)}")

        # Dodatkowe logowanie zawartości pliku
        logging.info(f"Zawartość pliku JSON: {json.dumps(data, indent=2)}")

        if not data:
            logging.error("Plik JSON jest pusty")
            return {"dzialy": []}

        if "dzialy" not in data:
            logging.error("Brak klucza 'dzialy' w pliku JSON")
            return {"dzialy": []}

        if not isinstance(data["dzialy"], list):
            logging.error("Klucz 'dzialy' nie jest listą")
            return {"dzialy": []}

        if not data["dzialy"]:
            logging.warning("Lista działów jest pusta")
            return {"dzialy": []}

        logging.info(f"Poprawnie załadowano {len(data['dzialy'])} działów")
        return data

    except FileNotFoundError:
        logging.error(f"Błąd: Plik {file_path} nie został znaleziony.")
    except json.JSONDecodeError as e:
        logging.error(f"Błąd: Plik {file_path} nie zawiera poprawnego formatu JSON. Szczegóły: {str(e)}")
    except Exception as e:
        logging.error(f"Nieoczekiwany błąd podczas ładowania pliku JSON: {str(e)}")
    
    return {"dzialy": []}

if __name__ == "__main__":
    # Użyj dokładnej ścieżki do pliku JSON
    prompts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'knowledge_base.json'))
    logging.info(f"Ścieżka do pliku knowledge_base.json: {prompts_path}")
    prompts = load_prompts(prompts_path)
    if "dzialy" in prompts:
        logging.info(f"Załadowano działy: {prompts['dzialy']}")
    else:
        logging.error("Nie udało się załadować działów z pliku JSON.")
