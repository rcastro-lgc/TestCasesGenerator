import os
from openai import OpenAI
from dotenv import load_dotenv
from app.db.model import Ticket
from app.config import MODEL_TESTCASES


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_test_cases(ticket: Ticket) -> list[str]:
    if not ticket.description or not ticket.title:
        return []

    prompt = f"""
    You are a senior QA analyst for a healthcare platform.
    Generate up to 5 functional test cases.
    Rules:
    - Include happy path and at least one negative/edge case.
    - Avoid redundancy; fewer than 5 is OK.
    - Output ONLY test cases, no extra text.
    - Each test case must follow exactly:
      Scenario: ...
      Action: ...
      Expected behavior: ...

    🔒 Use these exact labels: `Scenario:`, `Action:`, `Expected behavior:`  
    Do not use bold, italics, bullet points, or any other formatting.  
    Do not skip or merge lines. Each section must be on a separate line.

    ---
    Title: {ticket.title.strip()}
    Description: {ticket.description.strip()}
    Issue type: {ticket.issue_type}
    ---
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_TESTCASES,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        content = response.choices[0].message.content
        return [line.lstrip("-•0123456789. ").strip() for line in content.strip().split("\n") if line.strip()]
    except Exception as e:
        print(f"❌ Error generating test cases for {ticket.jira_key}: {e}")
        return []
