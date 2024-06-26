import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='../.env')

openai_api_key = os.getenv('OPENAI_API_KEY')

openai = OpenAI(api_key=openai_api_key)