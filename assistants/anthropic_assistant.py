import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(dotenv_path='../.env')

anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

anthropic = Anthropic(api_key=anthropic_api_key)

class AnthropicAssistant:
    def __init__(self, max_tokens: int=1024, temperature: float=0.2, system_prompt: str="Jesteś pomocnym asystentem"):
        self.client = anthropic
        self.messages = []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = system_prompt

    def add_user_message(self, user_message: str):
        self.messages.append(
            {"role": "user",
             "content": user_message}
        )
    
    def get_response(self, stream: bool=False) -> str:
        if not self.messages or self.messages[-1] == "assistant": 
            return "Error: No user message to respond to"

        if stream:
            return self._get_streamed_response
        else:
            return self._get_non_streamed_response
        
    def _get_non_streamed_response(self) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet@20240620",
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt
        )
        self.messages.append({"role": "assistant", "content": response.content[0].text})
        return response.content[0].text

    def _get_streamed_response(self) -> str:
        full_response = ""
        with self.client.messages.stream(
            model="claude-3-5-sonnet@20240620",
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
    
