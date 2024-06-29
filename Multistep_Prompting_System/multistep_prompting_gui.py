    import os
    import json
    import anthropic
    import PySimpleGUI as sg
    import threading
    import time
    from typing import Dict, Any

    # Konfiguracja klucza API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not ANTHROPIC_API_KEY:
        raise ValueError("Klucz API Anthropic nie został ustawiony. Ustaw zmienną środowiskową ANTHROPIC_API_KEY.")

    client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

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
        knowledge_base = load_knowledge_base('knowledge_base.json')
        if not knowledge_base:
            return "Nie można załadować bazy wiedzy. Sprawdź plik i spróbuj ponownie."

        # Krok 1: Generowanie wstępnej odpowiedzi
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
        sg.theme('LightBlue2')
        chat_layout = [
            [sg.Text('Multistep Prompting Chatbot', font=('Helvetica', 20), justification='center', expand_x=True)],
            [sg.HorizontalSeparator()],
            [sg.Text('Historia czatu', font=('Helvetica', 12))],
            [sg.Multiline(size=(60, 20), key='-CHAT-', disabled=True, font=('Helvetica', 12), autoscroll=True, background_color='#F0F0F0')],
            [sg.InputText(key='-QUERY-', size=(50, 1), font=('Helvetica', 12)),
             sg.Button('Wyślij', bind_return_key=True, font=('Helvetica', 12), button_color=('white', '#007ACC'))],
            [sg.Button('Wyczyść czat', font=('Helvetica', 12)), 
             sg.Button('Wyjście', font=('Helvetica', 12), button_color=('white', '#CC0000'))],
            [sg.Text('Status:', font=('Helvetica', 10)), 
             sg.Text('Gotowy', key='-STATUS-', font=('Helvetica', 10), text_color='green'),
             sg.Text('', key='-LOADING-', font=('Helvetica', 12), size=(2,1))]
        ]

        window = sg.Window('Multistep Prompting Chatbot', chat_layout, finalize=True, resizable=True)
        return window

    def loading_animation(window):
        animation = ['|', '/', '-', '\\']
        i = 0
        while True:
            if window['-STATUS-'].get() != 'Przetwarzanie...':
                break
            window['-LOADING-'].update(animation[i % len(animation)])
            window.refresh()
            time.sleep(0.1)
            i += 1

    def process_query(window, values):
        query = values['-QUERY-']
        window['-STATUS-'].update('Przetwarzanie...', text_color='orange')
        window['-CHAT-'].print(f"\nTy: {query}", text_color='blue')
        window['-QUERY-'].update('')
        window.refresh()

        threading.Thread(target=loading_animation, args=(window,), daemon=True).start()

        try:
            result = multistep_prompting(query)
            window['-CHAT-'].print(f"\nBot: {result}", text_color='green')
        except Exception as e:
            window['-CHAT-'].print(f"\nBot: Przepraszam, wystąpił błąd: {str(e)}", text_color='red')
        finally:
            window['-STATUS-'].update('Gotowy', text_color='green')
            window['-LOADING-'].update('')

    def run_gui():
        window = create_gui()

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == 'Wyjście':
                break
            if event == 'Wyślij' and values['-QUERY-'].strip():
                threading.Thread(target=process_query, args=(window, values), daemon=True).start()
            if event == 'Wyczyść czat':
                window['-CHAT-'].update('')
                window['-STATUS-'].update('Gotowy', text_color='green')
                window['-LOADING-'].update('')

        window.close()

    if __name__ == "__main__":
        run_gui()