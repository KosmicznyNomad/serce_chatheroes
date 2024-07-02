import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(dotenv_path='../.env')

anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

anthropic = Anthropic(api_key=anthropic_api_key)

class AnthropicAssistant:
    def __init__(self, max_tokens: int=1024, temperature: float=0.2, system_prompt: str="Jesteś pomocnym asystentem. Masz dostęp do narzędzi."):
        self.client = anthropic
        self.messages = []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.tools = [
        {
            "name": "baza_wiedzy",
            "description": "Uzyskaj dostęp do bazy wiedzy, aby zdobyć informacje na temat poruszony przez użytkownika. Jeśli znasz odpowiedź na pytanie, nie używaj bazy wiedzy.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pytanie": {
                        "type": "string",
                        "description": "Przekaż pytanie jakie zadał użytkownik",
                    }
                },
                "required": ["pytanie"],
            },
        }
    ]

    def add_user_message(self, user_message: str):
        self.messages.append(
            {"role": "user",
             "content": user_message}
        )
    
    def get_response(self, stream: bool=False) -> str:
        if not self.messages or self.messages[-1] == "assistant": 
            return "Error: No user message to respond to"

        if stream:
            return self._get_streamed_response()
        else:
            return self._get_non_streamed_response()
    
    def _handle_tool_use(self, tool_use):
        tool_name = tool_use.name
        tool_input = tool_use.input
        tool_id = tool_use.id

        self.messages.append({"role": "assistant", "content": [
            {"type": "tool_use", "id": tool_id, "name": tool_name, "input": tool_input}
            ]})

        if tool_name == "baza_wiedzy":
            result = f"Zapytanie: {tool_input['pytanie']} Odpowiedź z bazy danych: Kazik i Maja."
            self.messages.append({"role": "user", "content": [
                {"type": "tool_result", 
                 "tool_use_id": tool_id, 
                 "content": result}
                 ]})


    def _get_non_streamed_response(self) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt,
            tools=self.tools,
            tool_choice={"type": "auto"}
        )
        if response.stop_reason == "tool_use":
            self._handle_tool_use(response.content[-1])
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                messages=self.messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                tools=self.tools
            )
            self.messages.append({"role": "assistant", "content": response.content[0].text})
            return response.content[0].text
        elif response.stop_reason == "end_turn":
            self.messages.append({"role": "assistant", "content": response.content[0].text})
            return response.content[0].text

    def _get_streamed_response(self) -> str:
        full_response = ""
        with self.client.messages.stream(
            model="claude-3-5-sonnet-20240620",
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                yield text
        
        self.messages.append({"role": "assistant", "content": full_response})
        return full_response
    
    def clear_conversation(self) -> None:
        self.messages = []

    def get_conversation_history(self) -> list:
        return self.messages
    