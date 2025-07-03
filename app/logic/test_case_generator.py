"""
Main entry point for test case generation.
"""
from app.db.model import Ticket

def generate_test_cases(ticket: Ticket) -> list[str]:
    """Generate test cases using the Gemini AI model"""
    from app.logic.test_case_generator_gemini import generate_test_cases_with_gemini
    return generate_test_cases_with_gemini(ticket)
