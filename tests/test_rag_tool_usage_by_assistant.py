import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistants.anthropic_assistant import AnthropicAssistant


assistant = AnthropicAssistant(tool_use=True, system_prompt="Jesteś pomocnym asystentem. Masz dostęp do narzędzi.")

user_message = "Jakie są główne postacie w książce? Użyj narzędzi, baza wiedzy ma odpowiedź na to pytanie"

print("Test")
assistant.add_user_message(user_message)
response = assistant.get_response()
print(f"Result: {response}")

print("\nAnthropicAssistant conversation history:")
print(assistant.messages)