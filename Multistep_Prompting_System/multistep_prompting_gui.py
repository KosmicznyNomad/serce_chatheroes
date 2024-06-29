                        import PySimpleGUI as sg
                        from typing import Dict, Any
                        import json
                        import os
                        import anthropic
                        import threading
                        import time
                        from .agent_manager import AgentManager
                        from .agent_base import BaseAgent

                        __all__ = ['AgentManager', 'BaseAgent']
                        __version__ = "1.0.0"

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

                        class ChatbotGUI:
                            def __init__(self):
                                self.agent_manager = AgentManager()
                                self.window = None
                                self.knowledge_base = load_knowledge_base('knowledge_base.json')

                            def create_window(self):
                                sg.theme('LightBlue2')
                                dzialy = [dzial["nazwa"] for dzial in self.knowledge_base.get("dzialy", [])]
                                layout = [
                                    [sg.Text('Multistep Prompting Chatbot', font=('Helvetica', 20), justification='center', expand_x=True)],
                                    [sg.HorizontalSeparator()],
                                    [sg.Text('Wybierz dział:')],
                                    [sg.Combo(dzialy, key='-DZIAL-', default_value=dzialy[0] if dzialy else '', readonly=True)],
                                    [sg.Multiline(size=(60, 20), key='-CHAT-', disabled=True, font=('Helvetica', 12), autoscroll=True)],
                                    [sg.InputText(key='-QUERY-', size=(50, 1), font=('Helvetica', 12)),
                                     sg.Button('Wyślij', bind_return_key=True, font=('Helvetica', 12))],
                                    [sg.Button('Wyczyść czat', font=('Helvetica', 12)), 
                                     sg.Button('Wyjście', font=('Helvetica', 12))],
                                    [sg.Text('Status:', font=('Helvetica', 10)), 
                                     sg.Text('Gotowy', key='-STATUS-', font=('Helvetica', 10)),
                                     sg.Text('', key='-LOADING-', font=('Helvetica', 12), size=(2,1))]
                                ]
                                self.window = sg.Window('Multistep Prompting Chatbot', layout, finalize=True)

                            def loading_animation(self):
                                animation = ['|', '/', '-', '\\']
                                i = 0
                                while True:
                                    if self.window['-STATUS-'].get() != 'Przetwarzanie...':
                                        break
                                    self.window['-LOADING-'].update(animation[i % len(animation)])
                                    self.window.refresh()
                                    time.sleep(0.1)
                                    i += 1

                            def process_query(self, query: str, dzial: str):
                                self.window['-STATUS-'].update('Przetwarzanie...')
                                self.window['-CHAT-'].print(f"\nTy: {query}")
                                self.window['-QUERY-'].update('')
                                self.window.refresh()

                                threading.Thread(target=self.loading_animation, daemon=True).start()

                                try:
                                    result = self.agent_manager.multistep_prompting(f"[Dział: {dzial}] {query}")
                                    self.window['-CHAT-'].print(f"\nBot: {result}")
                                except Exception as e:
                                    self.window['-CHAT-'].print(f"\nBot: Przepraszam, wystąpił błąd: {str(e)}")
                                finally:
                                    self.window['-STATUS-'].update('Gotowy')
                                    self.window['-LOADING-'].update('')

                            def run(self):
                                self.create_window()

                                while True:
                                    event, values = self.window.read()
                                    if event == sg.WINDOW_CLOSED or event == 'Wyjście':
                                        break
                                    if event == 'Wyślij' and values['-QUERY-'].strip():
                                        query = values['-QUERY-']
                                        dzial = values['-DZIAL-']
                                        threading.Thread(target=self.process_query, args=(query, dzial), daemon=True).start()
                                    if event == 'Wyczyść czat':
                                        self.window['-CHAT-'].update('')
                                        self.window['-STATUS-'].update('Gotowy')
                                        self.window['-LOADING-'].update('')

                                self.window.close()

                        if __name__ == "__main__":
                            chatbot_gui = ChatbotGUI()
                            chatbot_gui.run()