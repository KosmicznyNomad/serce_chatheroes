# Serce Chatheroes

This project implements an AI assistant system using multiple language models and RAG (Retrieval-Augmented Generation) functionality.

## Features

- Multiple AI assistants (OpenAI and Anthropic)
- Agent-based architecture
- RAG (Retrieval-Augmented Generation) functionality
- Customizable prompts

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-assistant-project.git
cd ai-assistant-project
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows, use 
venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   Create a `.env` file in the project root and add your API keys:

```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```