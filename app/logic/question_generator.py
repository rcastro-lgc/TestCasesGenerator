import os
from openai import OpenAI
from app.db.model import Ticket
from dotenv import load_dotenv
from app.config import MODEL_QUESTIONS

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_questions(ticket: Ticket) -> list[str]:
    if not ticket.description or not ticket.title:
        return []

    prompt = f"""
    You are a QA assistant working on a healthcare platform.

    Your task is to help the QA team **define 3 to 5 smart questions** before implementing the following Jira ticket.

    ---
    Title: {ticket.title.strip()}
    Description: {ticket.description.strip()}
    Issue type: {ticket.issue_type}
    ---

    The goal is to uncover:
    - Possible edge cases or system dependencies
    - Risky assumptions or vague requirements
    - Clinical or workflow-specific considerations
    - Scenarios that could break under real-world usage

    Return the questions in clear English as a bullet list.
    Do not include any explanation or commentary—only the questions.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_QUESTIONS,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        return [line.lstrip("-•0123456789. ").strip() for line in content.strip().split("\n") if line.strip()]
    except Exception as e:
        print(f"❌ Error generating questions for {ticket.jira_key}: {e}")
        return []
