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
    user_message = "What's the capital of France?"

    # Test AnthropicAssistant
    print("Testing AnthropicAssistant:")
    anthropic_assistant.add_user_message(user_message)
    anthropic_response = anthropic_assistant.get_response(stream=True)
    print("Anthropic streamed response:")
    for chunk in anthropic_response:  # Remove the parentheses here
        print(chunk, end='', flush=True)
    print()

    # Test OpenAIAssistant
    print("\nTesting OpenAIAssistant:")
    openai_assistant.add_user_message(user_message)
    openai_response = openai_assistant.get_response(stream=True)
    print("OpenAI streamed response:")
    for chunk in openai_response:  # Remove the parentheses here as well
        print(chunk, end='', flush=True)
    print()

    # Test conversation history
    print("\nAnthropicAssistant conversation history:")
    print(anthropic_assistant.get_conversation_history())

    print("\nOpenAIAssistant conversation history:")
    print(openai_assistant.get_conversation_history())


if __name__ == "__main__":
    test_assistants()