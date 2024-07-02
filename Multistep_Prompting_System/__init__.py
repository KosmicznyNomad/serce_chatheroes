import PySimpleGUI as sg
from typing import Dict, Any
import json
import os
import sys
sys.path.append('.')
from .agent_manager import AgentManager
from .agent_base import BaseAgent

__all__ = ['AgentManager', 'BaseAgent']
__version__ = "1.0.0"

# Zamiast importować z nieistniejących plików, zdefiniujmy te funkcje tutaj
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

def multistep_prompting(query: str, dzial: str) -> str:
    # Tu implementacja logiki multistep prompting
    # Na razie zwróćmy przykładową odpowiedź
    return f"Odpowiedź na pytanie '{query}' z działu '{dzial}'"

def create_gui():
    sg.theme('LightBlue2')
    knowledge_base = load_knowledge_base('knowledge_base.json')
    dzialy = [dzial["nazwa"] for dzial in knowledge_base.get("dzialy", [])]

    layout = [
        [sg.Text('Wybierz dział:')],
        [sg.Combo(dzialy, key='-DZIAL-', default_value=dzialy[0] if dzialy else '', readonly=True)],
        [sg.Text('Wprowadź swoje pytanie:')],
        [sg.InputText(key='-QUERY-', size=(50, 1))],
        [sg.Button('Zapytaj', bind_return_key=True), sg.Button('Wyjście')],
        [sg.Multiline(size=(50, 10), key='-OUTPUT-', disabled=True)]
        ]

    window = sg.Window('System Multistep Prompting - Bot Edukacyjny', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Wyjście':
            break
        if event == 'Zapytaj':
            query = values['-QUERY-']
            dzial = values['-DZIAL-']
            window['-OUTPUT-'].update('Przetwarzanie pytania...')
            try:
                result = multistep_prompting(query, dzial)
                window['-OUTPUT-'].update(result)
            except Exception as e:
                window['-OUTPUT-'].update(f"Wystąpił błąd: {str(e)}")

        window.close()

    if __name__ == "__main__":
        create_gui()
