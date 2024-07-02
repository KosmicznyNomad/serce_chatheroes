import os
import logging
from agent_manager import AgentManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def test_agent_manager():
    try:
        agent_manager = AgentManager()
        logging.info("AgentManager został pomyślnie utworzony.")
        
        # Przykładowe dane do testowania
        query = "Co to jest składnia?"
        dzial_name = "Gramatyka dla klasy 4 szkoły podstawowej"
        dzial_info = None

        # Znajdź dział w załadowanych promptach
        for dzial in agent_manager.prompts.get('dzialy', []):
            if dzial['nazwa'] == dzial_name:
                dzial_info = dzial
                break

        if dzial_info:
            response = agent_manager.multistep_prompting(query, dzial_info)
            logging.info(f"Odpowiedź: {response}")
        else:
            logging.error(f"Nie znaleziono działu o nazwie: {dzial_name}")
    except Exception as e:
        logging.error(f"Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    test_agent_manager()
