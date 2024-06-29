import os
import json
import anthropic
import PySimpleGUI as sg
from typing import Dict, Any

# Konfiguracja klucza API z zmiennej środowiskowej
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Client(api_key=anthropic_api_key)

def load_knowledge_base(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Błąd: Plik {file_path} nie został znaleziony.")
        return {}
    except json.JSONDecodeError:
        print(f"Błąd: Plik {file_path} nie zawiera poprawnego formatu JSON.")
        return {}

def generate_response(prompt: str, max_tokens: int) -> str:
    try:
        response = client.completion(
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
            model="claude-2",
            max_tokens_to_sample=max_tokens,
            temperature=0.7,
        )
        return response.completion.strip()
    except anthropic.APIError as e:
        print(f"Błąd podczas generowania odpowiedzi: {e}")
        return ""

def multistep_prompting(initial_query: str) -> str:
    if not anthropic_api_key:
        raise ValueError("Klucz API Anthropic nie został ustawiony. Ustaw zmienną środowiskową ANTHROPIC_API_KEY.")

    knowledge_base = load_knowledge_base('knowledge_base.json')

    if not knowledge_base:
        return "Nie można załadować bazy wiedzy. Sprawdź plik i spróbuj ponownie."

    # Krok 1: Generowanie wstępnej odpowiedzi na pytanie użytkownika
    step1_prompt = f"Odpowiedz zwięźle na następujące pytanie: {initial_query}"
    step1_response = generate_response(step1_prompt, max_tokens=150)

    if not step1_response:
        return "Nie udało się wygenerować wstępnej odpowiedzi."

    # Krok 2: Sprawdzenie zgodności z bazą wiedzy
    step2_prompt = f"""
    Sprawdź, czy poniższa odpowiedź jest zgodna z zakresem wiedzy zawartym w bazie wiedzy:

    Pytanie: {initial_query}
    Odpowiedź: {step1_response}

    Baza wiedzy: {json.dumps(knowledge_base, ensure_ascii=False)}

    Odpowiedz krótko 'Tak' lub 'Nie', a następnie krótko uzasadnij swoją odpowiedź.
    """
    step2_response = generate_response(step2_prompt, max_tokens=100)

    if not step2_response:
        return "Nie udało się zweryfikować odpowiedzi."

    # Krok 3: Przeformułowanie odpowiedzi stylem nauczyciela poety
    step3_prompt = f"""
    Jesteś nauczycielem poetą. Przeformułuj poniższą odpowiedź na pytanie, używając poetyckiego, inspirującego stylu:

    Pytanie: {initial_query}
    Oryginalna odpowiedź: {step1_response}
    Weryfikacja zgodności: {step2_response}

    Przygotuj końcową, poetycką odpowiedź, zachowując merytoryczną treść.
    """
    final_response = generate_response(step3_prompt, max_tokens=200)

    if not final_response:
        return "Nie udało się sformułować końcowej odpowiedzi."

    return final_response

def create_gui():
    sg.theme('LightBlue2')  # Ustaw motyw

    layout = [
        [sg.Text('Wprowadź swoje pytanie:')],
        [sg.InputText(key='-QUERY-', size=(50, 1))],
        [sg.Button('Zapytaj', bind_return_key=True), sg.Button('Wyjście')],
        [sg.Multiline(size=(50, 10), key='-OUTPUT-', disabled=True)]
    ]

    window = sg.Window('System Multistep Prompting', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Wyjście':
            break
        if event == 'Zapytaj':
            query = values['-QUERY-']
            window['-OUTPUT-'].update('Przetwarzanie pytania...')
            try:
                result = multistep_prompting(query)
                window['-OUTPUT-'].update(result)
            except Exception as e:
                window['-OUTPUT-'].update(f"Wystąpił błąd: {str(e)}")

    window.close()

if __name__ == "__main__":
    create_gui()