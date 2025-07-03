"""
Main entry point for question generation.
"""
from app.db.model import Ticket
from app.config import API_PROVIDER

def generate_questions(ticket: Ticket) -> list[str]:
    """Generate questions using the Gemini AI model"""
    from app.logic.question_generator_gemini import generate_questions_with_gemini
    return generate_questions_with_gemini(ticket)
