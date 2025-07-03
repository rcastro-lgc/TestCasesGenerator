import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Models by task type
MODEL_QUESTIONS = os.getenv("MODEL_QUESTIONS", "gemini-1.5-pro")
MODEL_TESTCASES = os.getenv("MODEL_TESTCASES", "gemini-1.5-flash")

# API Provider
API_PROVIDER = "gemini"