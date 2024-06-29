import anthropic
import os

class BaseAgent:
    def __init__(self):
        self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_response(self, prompt: str, model: str = "claude-3-5-sonnet-202406209") -> str:
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                    ]
                )
            return response.content[0].text
        except anthropic.APIError as e:
            print(f"Błąd podczas generowania odpowiedzi: {e}")
            return ""