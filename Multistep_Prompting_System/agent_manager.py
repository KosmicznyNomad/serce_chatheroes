        from .agent_base import BaseAgent
        import json
        from typing import Dict, Any

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
                step1_prompt = f"Odpowiedz na następujące pytanie: {initial_query}"
                step1_response = self.generate_response(step1_prompt)

                if not step1_response:
                    return "Nie udało się wygenerować wstępnej odpowiedzi."

                # Krok 2: Weryfikacja odpowiedzi na podstawie bazy wiedzy
                step2_prompt = f"""
                Zweryfikuj poniższą odpowiedź na podstawie dostępnej bazy wiedzy:

                Pytanie: {initial_query}
                Odpowiedź: {step1_response}

                Baza wiedzy: {json.dumps(self.knowledge_base, ensure_ascii=False)}

                Czy odpowiedź jest zgodna z bazą wiedzy? Jeśli nie, zaproponuj poprawki.
                """
                step2_response = self.generate_response(step2_prompt)

                if not step2_response:
                    return "Nie udało się zweryfikować odpowiedzi."

                # Krok 3: Finalna formulacja odpowiedzi
                step3_prompt = f"""
                Na podstawie pierwotnej odpowiedzi i weryfikacji, sformułuj finalną odpowiedź:

                Pierwotna odpowiedź: {step1_response}
                Weryfikacja: {step2_response}

                Przygotuj końcową, spójną odpowiedź na pytanie: {initial_query}
                """
                final_response = self.generate_response(step3_prompt)

                if not final_response:
                    return "Nie udało się sformułować końcowej odpowiedzi."

                return final_response