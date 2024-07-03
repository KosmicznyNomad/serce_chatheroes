import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

from assistants.anthropic_assistant import AnthropicAssistant

class ChatDatabase:
    def __init__(self, db_name="chat_history.db"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, db_name)

        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def save_message(self, role, content):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
        self.conn.commit()
    
    def load_messages(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT role, content FROM messages ORDER BY id")
        return [{"role": role, "content": content} for role, content in cursor.fetchall()]
    
    def clear_messages(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages")
        self.conn.commit()
    
    def close(self):
        self.conn.close()

def chat_system():
    assistant = AnthropicAssistant()
    db = ChatDatabase()

    previous_messages = db.load_messages()
    # print(previous_messages)
    assistant.messages = previous_messages
    for message in previous_messages:
        if message["role"] == "user":
            print(f"You: {message['content']}")
        elif message["role"] == "assistant":
            print(f"Assistant: {message['content']}")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'clear':
            assistant.clear_conversation()
            db.clear_messages()
            print("Conversation history cleared")
            continue

        assistant.add_user_message(user_input)
        db.save_message('user', user_input)

        response = assistant.get_response()
        print(f"Assistant: {response}")
        db.save_message('assistant', response)

    db.close()

if __name__ == "__main__":
    chat_system()