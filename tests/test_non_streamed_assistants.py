import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from assistants.anthropic_assistant import AnthropicAssistant
from assistants.openai_assistant import OpenAIAssistant

def test_assistants():
    # Initialize both assistants
    anthropic_assistant = AnthropicAssistant()
    openai_assistant = OpenAIAssistant()

    # Test message
    user_message = "Jakie miasto jest stolicą Polski?"

    # Test AnthropicAssistant
    print("Testing AnthropicAssistant:")
    anthropic_assistant.add_user_message(user_message)
    anthropic_response = anthropic_assistant.get_response()
    print(f"Anthropic response: {anthropic_response}")

    # Test OpenAIAssistant
    print("\nTesting OpenAIAssistant:")
    openai_assistant.add_user_message(user_message)
    openai_response = openai_assistant.get_response()
    print(f"OpenAI response: {openai_response}")

    # Test conversation history
    print("\nAnthropicAssistant conversation history:")
    print(anthropic_assistant.get_conversation_history())

    print("\nOpenAIAssistant conversation history:")
    print(openai_assistant.get_conversation_history())

    # Test clearing conversation
    anthropic_assistant.clear_conversation()
    openai_assistant.clear_conversation()

    print("\nAfter clearing conversations:")
    print("AnthropicAssistant conversation history:", anthropic_assistant.get_conversation_history())
    print("OpenAIAssistant conversation history:", openai_assistant.get_conversation_history())

if __name__ == "__main__":
    test_assistants()