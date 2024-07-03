import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistants.anthropic_assistant import AnthropicAssistant

assistant = AnthropicAssistant(tool_use=True, system_prompt="Jesteś pomocnym asystentem. Masz dostęp do narzędzi")

query = "Opowiedz mi krótką historyjkę dla dzieci. Imiona bohaterów znajdują się w bazie wiedzy"

assistant.add_user_message(query)

response = assistant.get_response(stream=True)

for chunk in response:
    print(chunk, end="")
print()

print()
history = assistant.get_conversation_history()
print(history)