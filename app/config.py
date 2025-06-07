import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Modelos por tipo de tarea
MODEL_QUESTIONS = os.getenv("OPENAI_MODEL_QUESTIONS", "gpt-4-turbo")
MODEL_TESTCASES = os.getenv("OPENAI_MODEL_TESTCASES", "gpt-3.5-turbo")