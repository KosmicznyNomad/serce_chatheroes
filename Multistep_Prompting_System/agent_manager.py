import json
from typing import Dict, Any
from .agent_base import BaseAgent

class AgentManager(BaseAgent):
    def __init__(self):
        super().__init__()
        self.knowledge_base = self.load_knowledge_base('knowledge_base.json')

    def load_knowledge_base(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Błąd: Plik {file_path} nie został znaleziony.")
            return {}
        except json.JSONDecodeError:
            print(f"Błąd: Plik {file_path} nie zawiera poprawnego formatu JSON.")
            return {}

    def multistep_prompting(self, initial_query: str) -> str:
        # Krok 1: Generowanie wstępnej odpowiedzi
        step1_response = self._generate_initial_response(initial_query)
        if not step1_response:
            return "Nie udało się wygenerować wstępnej odpowiedzi."

        # Krok 2: Weryfikacja odpowiedzi na podstawie bazy wiedzy
        step2_response = self._verify_response(initial_query, step1_response)
        if not step2_response:
            return "Nie udało się zweryfikować odpowiedzi."

        # Krok 3: Finalna formulacja odpowiedzi
        final_response = self._formulate_final_response(initial_query, step1_response, step2_response)
        if not final_response:
            return "Nie udało się sformułować końcowej odpowiedzi."

        return final_response

    def _generate_initial_response(self, query: str) -> str:
        prompt = f"Odpowiedz na następujące pytanie: {query}"
        return self.generate_response(prompt)

    def _verify_response(self, query: str, initial_response: str) -> str:
        prompt = f"""
        Zweryfikuj poniższą odpowiedź na podstawie dostępnej bazy wiedzy:

        Pytanie: {query}
        Odpowiedź: {initial_response}

        Baza wiedzy: {json.dumps(self.knowledge_base, ensure_ascii=False)}

        Czy odpowiedź jest zgodna z bazą wiedzy? Jeśli nie, zaproponuj poprawki.
        """
        return self.generate_response(prompt)

    def _formulate_final_response(self, query: str, initial_response: str, verification: str) -> str:
        prompt = f"""
        Na podstawie pierwotnej odpowiedzi i weryfikacji, sformułuj finalną odpowiedź:

        Pierwotna odpowiedź: {initial_response}
        Weryfikacja: {verification}

        Przygotuj końcową, spójną odpowiedź na pytanie: {query}
        """
        return self.generate_response(prompt)