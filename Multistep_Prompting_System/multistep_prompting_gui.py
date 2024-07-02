import os
import json
import logging
import PySimpleGUI as sg
import threading
import time  
from typing import Dict, Any
from agent_manager import AgentManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ChatbotGUI:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.window = None
        prompts_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
        logging.info(f"Ścieżka do pliku knowledge_base.json: {os.path.abspath(prompts_path)}")
        self.prompts = self.load_prompts(prompts_path)
        logging.info(f"Załadowane prompty: {json.dumps(self.prompts, indent=2)}")
        
        if not self.prompts.get("dzialy"):
            logging.error("Brak działów w załadowanych promptach")
        else:
            logging.info(f"Liczba załadowanych działów: {len(self.prompts['dzialy'])}")

        self.theme()

    def load_prompts(self, file_path: str) -> Dict[str, Any]:
        logging.info(f"Próba otwarcia pliku: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                logging.info("Plik otwarty pomyślnie")
                data = json.load(file)
                logging.info("JSON załadowany pomyślnie")
                logging.info(f"Struktura JSON: {json.dumps(data, indent=2)}")

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

    def theme(self):
        sg.LOOK_AND_FEEL_TABLE['MickiewiczTheme'] = {
            'BACKGROUND': '#F0E6D2',
            'TEXT': '#4A3933',
            'INPUT': '#D7C9B8',
            'TEXT_INPUT': '#4A3933',
            'SCROLL': '#966F33',
            'BUTTON': ('#FFFFFF', '#8B4513'),
            'PROGRESS': ('#D1826B', '#CC8019'),
            'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
        }
        sg.theme('MickiewiczTheme')

    def create_window(self):
        dzialy = [dzial["nazwa"] for dzial in self.prompts.get("dzialy", [])]
        logging.info(f"Liczba działów znalezionych w self.prompts: {len(dzialy)}")
        logging.info(f"Znalezione działy: {dzialy}")
        
        if not dzialy:
            dzialy = ["Brak dostępnych działów"]
            logging.warning("Brak dostępnych działów w pliku JSON.")

        chat_area = [
            [sg.Multiline(size=(60, 20), key='-CHAT-', disabled=True, font=('Garamond', 12), background_color='#F7F1E5', text_color='#4A3933', autoscroll=True)],
            [sg.InputText(key='-QUERY-', size=(50, 1), font=('Garamond', 12), background_color='#F7F1E5'),
             sg.Button('Napisz', bind_return_key=True, font=('Garamond', 12), button_color=('#FFFFFF', '#8B4513'))]
        ]

        controls = [
            [sg.Text('Wybierz dział:', font=('Garamond', 12))],
            [sg.Combo(dzialy, key='-DZIAL-', default_value=dzialy[0], readonly=True, font=('Garamond', 12), enable_events=True)],
            [sg.Text('Opis działu:', font=('Garamond', 10))],
            [sg.Multiline('', key='-OPIS-DZIALU-', size=(50, 4), font=('Garamond', 10), disabled=True)],
            [sg.Button('Wyczyść kartę', font=('Garamond', 12), button_color=('#FFFFFF', '#8B4513')),
             sg.Button('Opuść salon', font=('Garamond', 12), button_color=('#FFFFFF', '#8B4513'))],
            [sg.Text('Status:', font=('Garamond', 10)),
             sg.Text('Gotowy', key='-STATUS-', font=('Garamond', 10)),
             sg.Text('', key='-LOADING-', font=('Garamond', 12), size=(2,1))]
        ]

        layout = [
            [sg.Text('Salon Poetycki Adama Mickiewicza', font=('Garamond', 24, 'bold'), justification='center', expand_x=True)],
            [sg.HorizontalSeparator()],
            [sg.Column(chat_area)],
            [sg.Column(controls, justification='center', element_justification='center')]
        ]

        self.window = sg.Window('Salon Poetycki Adama Mickiewicza', layout, finalize=True, resizable=True)
        logging.info("Okno GUI zostało utworzone.")

    def loading_animation(self):
        animation = ['✒️', '📜', '🖋️', '📖']
        i = 0
        while True:
            if self.window['-STATUS-'].get() != 'Tworzy...':
                break
            self.window['-LOADING-'].update(animation[i % len(animation)])
            self.window.refresh()
            time.sleep(0.2)
            i += 1

    def process_query(self, query: str, dzial: str):
        if not self.agent_manager:
            self.window['-CHAT-'].print("\nBłąd: Agent Manager nie został zainicjalizowany.")
            logging.error("Próba przetworzenia zapytania bez zainicjalizowanego AgentManager.")
            return

        self.window['-STATUS-'].update('Tworzy...')
        self.window['-CHAT-'].print(f"\nTy: {query}")
        self.window['-QUERY-'].update('')
        self.window.refresh()

        threading.Thread(target=self.loading_animation, daemon=True).start()

        try:
            logging.info(f"Próba przetworzenia zapytania: {query} dla działu: {dzial}")
            dzial_info = self.get_dzial_info(dzial)
            logging.info(f"Informacje o wybranym dziale: {json.dumps(dzial_info, indent=2)}")
            result = self.agent_manager.process_query(query, dzial_info)
            logging.info(f"Otrzymana odpowiedź: {result}")
            self.window['-CHAT-'].print(f"\nMickiewicz: {result}")
            logging.info(f"Zapytanie przetworzone pomyślnie. Dział: {dzial}")
        except Exception as e:
            error_message = f"\nMickiewicz: Wybacz, przyjacielu, ale muza mnie opuściła: {str(e)}"
            self.window['-CHAT-'].print(error_message)
            logging.error(f"Błąd podczas przetwarzania zapytania: {str(e)}", exc_info=True)
        finally:
            self.window['-STATUS-'].update('Gotowy')
            self.window['-LOADING-'].update('')

    def get_dzial_info(self, dzial_name: str) -> Dict[str, Any]:
        for dzial in self.prompts.get("dzialy", []):
            if dzial["nazwa"] == dzial_name:
                return dzial
        return {}

    def run(self):
        self.create_window()
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED or event == 'Opuść salon':
                break
            if event == 'Napisz' and values['-QUERY-'].strip():
                query = values['-QUERY-']
                dzial = values['-DZIAL-']
                logging.info(f"Wybrano dział: {dzial}")
                threading.Thread(target=self.process_query, args=(query, dzial), daemon=True).start()
            if event == 'Wyczyść kartę':
                self.window['-CHAT-'].update('')
                self.window['-STATUS-'].update('Gotowy')
                self.window['-LOADING-'].update('')
            if event == '-DZIAL-':
                selected_dzial = values['-DZIAL-']
                dzial_info = self.get_dzial_info(selected_dzial)
                description = dzial_info.get("opis", "Brak opisu")
                logging.info(f"Zmieniono dział na: {selected_dzial}")
                logging.info(f"Opis wybranego działu: {description}")
                self.window['-OPIS-DZIALU-'].update(description)
        
        self.window.close()

if __name__ == "__main__":
    # Sprawdzenie, czy klucz API jest dostępny
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logging.warning("UWAGA: Klucz API Anthropic nie został znaleziony w zmiennych środowiskowych.")
        logging.warning("Upewnij się, że plik .env jest poprawnie skonfigurowany.")
    else:
        logging.info("Klucz API Anthropic został pomyślnie załadowany.")

    try:
        logging.info("Próba utworzenia instancji ChatbotGUI")
        chatbot_gui = ChatbotGUI()
        logging.info("Instancja ChatbotGUI utworzona pomyślnie")
        logging.info("Próba uruchomienia ChatbotGUI")
        chatbot_gui.run()
    except ValueError as e:
        logging.error(f"Błąd inicjalizacji GUI: {str(e)}")
        print(f"Nie można uruchomić aplikacji: {str(e)}")
    except Exception as e:
        logging.error(f"Wystąpił nieoczekiwany błąd: {str(e)}", exc_info=True)
        print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
