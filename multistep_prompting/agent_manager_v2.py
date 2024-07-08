import sys
import os
import json
from typing import Dict, Any, Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistants.anthropic_assistant import AnthropicAssistant

class AgentManager():
    def __init__(self):
        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'knowledge_base.json'))
        self.prompts = self.load_prompts(json_path)
        self.nauczyciel = AnthropicAssistant(system_prompt="Jesteś nauczycielem z wieloletnim doświadczeniem")
        self.postac = AnthropicAssistant(system_prompt="Jesteś Adamem Mickiewiczem")

    def load_prompts(self, file_path: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # if not self.validate_json_structure(data):
                #     return None
                
                return data
        except json.JSONDecodeError as e:
            print(f"Błąd dekodowania JSON: {str(e)}")

    def process_query(self, query: str, dzial_info: Dict[str, Any]) -> str:
        return self.multistep_prompting(query, dzial_info)

    def multistep_prompting(self, query: str, dzial_info: Dict[str, Any]) -> str:
        if not dzial_info:
            return "Przepraszam, ale nie mam wystarczających informacji, aby odpowiedzieć na Twoje pytanie."

        # Pierwszy krok: uzyskanie odpowiedzi z bazy wiedzy JSON
        initial_response = self._process_query(query, dzial_info, step="initial")
        if not initial_response:
            return "Nie udało się przetworzyć zapytania."

        # Drugi krok: stylizowanie odpowiedzi na Mickiewicza
        followup_query = f"Na podstawie odpowiedzi: {initial_response}, przetwórz odpowiedź na pytanie: {query}"
        followup_response = self._process_query(followup_query, dzial_info, step="followup", initial_response=initial_response)

        final_response = f"Pytanie ucznia: {query}\n\nOdpowiedź: {followup_response}"
        return final_response
        

    def _process_query(self, query: str, dzial_info: Dict[str, Any], step: str, initial_response: str = "") -> str:
        if step == "initial":
            prompt = f"""
            Jako nauczyciel z wieloletnim doświadczeniem, wypisz kluczowe informacje z programu szkolnego, które są wymagane do omówienia tego działu. Uwzględnij ciekawostkę oraz kluczowe dane. 
            Dział: {dzial_info['nazwa']}
            Opis działu: {dzial_info['opis']}
            Tematy:
            {self._format_topics(dzial_info.get('tematy', []))}
            Pytanie ucznia: {query}
            Odpowiedź:
            """
            self.nauczyciel.add_user_message(prompt)
            response = self.nauczyciel.get_response()
        elif step == "followup":
            prompt = f"""
            Zamień odpowiedź z pierwszego kroku w zrozumiałą odpowiedź na pytanie ucznia. Wykorzystaj techniki prezentowania informacji najlepszych nauczycieli, którzy tłumaczą materiał za pomocą zrozumiałych analogii. Pisz w pierwszej osobie jako Adam Mickiewicz, poeta, który korzysta z współczesnego słownictwa przystępnego dla dyslektyków. Pisz tekst w formie pierwszoosobowej. Skorzystaj miejscami z humoru.         
            Odpowiedź z pierwszego kroku: {initial_response}
            Pytanie ucznia: {query}
            Twoja odpowiedź:
            """
            self.postac.add_user_message(prompt)
            response = self.postac.get_response()
        else:
            return "Przepraszam, wystąpił błąd w przetwarzaniu zapytania."

        return response

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

    def change_default_model(self, new_model: str):
        self.default_model = new_model