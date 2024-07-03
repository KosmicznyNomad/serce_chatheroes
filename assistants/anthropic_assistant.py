import os
from dotenv import load_dotenv
from anthropic import Anthropic
import json

load_dotenv(dotenv_path='../.env')

anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

anthropic = Anthropic(api_key=anthropic_api_key)

class AnthropicAssistant:
    def __init__(self, max_tokens: int=1024, temperature: float=0.2, system_prompt: str="Jesteś pomocnym asystentem. Masz dostęp do narzędzi.", tool_use: bool=False):
        self.client = anthropic
        self.messages = []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.tool_use = tool_use
        self.tools = [
        {
            "name": "baza_wiedzy",
            "description": "Uzyskaj dostęp do bazy wiedzy, aby zdobyć informacje na temat poruszony przez użytkownika. Jeśli znasz odpowiedź na pytanie, nie używaj bazy wiedzy. Jeśli nie znasz, musisz użyć bazy wiedzy..",
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
        kwargs = {
            "model": "claude-3-5-sonnet-20240620",
            "messages": self.messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": self.system_prompt,
        }

        if self.tool_use:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = {"type": "auto"}

        response = self.client.messages.create(**kwargs)

        if self.tool_use and response.stop_reason == "tool_use":
            self._handle_tool_use(response.content[-1])
            response = self.client.messages.create(**kwargs)
        
        if response.stop_reason == "end_turn":
            self.messages.append({"role": "assistant", "content": response.content[0].text})
            return response.content[0].text

    def _get_streamed_response(self) -> str:
        full_response = ""
        kwargs = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": self.system_prompt,
        }

        if self.tool_use:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = {"type": "auto"}

        with self.client.messages.create(
            messages=self.messages,
            stream=True,
            **kwargs
        ) as stream:
            current_tool_use = None
            tool_input_json = ""

            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        current_tool_use = event.content_block
                        tool_input_json = ""
                elif event.type == "content_block_delta":
                    if current_tool_use and event.delta.type == "input_json_delta":
                        tool_input_json += event.delta.partial_json
                    elif event.delta.type == "text_delta":
                        text = event.delta.text
                        full_response += text
                        yield text
                elif event.type == "content_block_stop":
                    if current_tool_use:
                        try:
                            tool_input = json.loads(tool_input_json)
                            current_tool_use.input = tool_input
                            self._handle_tool_use(current_tool_use)
                            with self.client.messages.stream(
                                messages=self.messages,
                                **kwargs
                            ) as stream:
                                for chunk in stream.text_stream:
                                    yield chunk
                                    full_response += chunk
                        except json.JSONDecodeError:
                            print(f"Error decoding tool input JSON: {tool_input_json}")
                        finally:
                            current_tool_use = None
                            tool_input_json = ""

        self.messages.append({"role": "assistant", "content": full_response})
        return full_response
    
    def clear_conversation(self) -> None:
        self.messages = []

    def get_conversation_history(self) -> list:
        return self.messages
    