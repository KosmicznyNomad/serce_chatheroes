import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='../.env')

openai_api_key = os.getenv('OPENAI_API_KEY')

openai = OpenAI(api_key=openai_api_key)

class OpenAIAssistant:
    def __init__(self, max_tokens: int=1024, temperature: float=0.2, system_prompt: str="Jesteś pomocnym asystentem"):
        self.client = openai
        self.messages = []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.messages.append({"role": "system", "content": system_prompt})
    
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
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        self.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        return response.choices[0].message.content
    
    def _get_streamed_response(self) -> str:
        full_response = ""
        for chunk in self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True
        ):
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        self.messages.append({"role": "assistant", "content": full_response})
        return full_response
    
    def clear_conversation(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def get_conversation_history(self) -> list:
        return self.messages
    