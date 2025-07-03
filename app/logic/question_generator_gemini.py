import os
import time
import random
import google.generativeai as genai
from app.db.model import Ticket
from dotenv import load_dotenv
from app.config import MODEL_QUESTIONS, GOOGLE_API_KEY, API_PROVIDER

load_dotenv()

# Configure the Gemini API
if not GOOGLE_API_KEY or GOOGLE_API_KEY in ["your-google-api-key-here", "YOUR_ACTUAL_GOOGLE_API_KEY_HERE"]:
    print("⚠️ WARNING: GOOGLE_API_KEY is not set or is using a placeholder value")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"⚠️ WARNING: Error configuring Google Generative AI: {e}")

def generate_questions_with_gemini(ticket: Ticket) -> list[str]:
    """Generate questions using Google's Gemini models"""
    # Check if API key is set and valid
    if not GOOGLE_API_KEY or GOOGLE_API_KEY in ["your-google-api-key-here", "YOUR_ACTUAL_GOOGLE_API_KEY_HERE"]:
        print(f"❌ GOOGLE_API_KEY is not properly set in .env file")
        return [
            "Missing Google API key. Please set a valid GOOGLE_API_KEY in your .env file.",
            "See the README for instructions on obtaining and configuring a Google API key."
        ]
    
    # Check if ticket has description and title (safely for SQLAlchemy)
    if ticket.description is None or ticket.title is None:
        return []
    
    # Convert SQLAlchemy objects to strings for safe handling
    ticket_title = str(ticket.title)
    ticket_description = str(ticket.description)
    ticket_issue_type = str(ticket.issue_type) if ticket.issue_type is not None else "Task"
    
    if not ticket_title.strip() or not ticket_description.strip():
        return []
    
    prompt = f"""
    You are a QA assistant working on a healthcare platform.

    Your task is to help the QA team **define 3 to 5 smart questions** before implementing the following Jira ticket.

    ---
    Title: {ticket_title}
    Description: {ticket_description}
    Issue type: {ticket_issue_type}
    ---

    The goal is to uncover:
    - Possible edge cases or system dependencies
    - Risky assumptions or vague requirements
    - Clinical or workflow-specific considerations
    - Scenarios that could break under real-world usage

    Return the questions in clear English as a bullet list.
    Do not include any explanation or commentary—only the questions.
    """
    
    # Models to try in fallback sequence
    models_to_try = [
        MODEL_QUESTIONS,
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]
    
    # Max retries per model
    max_retries = 2
    last_error = None
    
    # Try each model in sequence
    for model_name in models_to_try:
        # Try with retries for each model
        for attempt in range(max_retries):
            try:
                print(f"Attempting to generate questions with Gemini model: {model_name} (attempt {attempt+1}/{max_retries})")
                
                try:
                    # Create a Gemini model - The API may have changed since this code was written
                    # Try different methods to ensure compatibility
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                    except AttributeError:
                        # If GenerativeModel is not available, try older API patterns
                        model = genai.get_model(model_name)
                        response = model.generate_text(prompt)
                    
                    if hasattr(response, 'text'):
                        content = response.text
                    elif hasattr(response, 'content'):
                        content = response.content
                    else:
                        content = str(response)
                        
                    return [line.lstrip("-•0123456789. ").strip() for line in content.strip().split("\n") if line.strip()]
                except Exception as model_error:
                    raise Exception(f"Error with model execution: {str(model_error)}")
                
            except Exception as e:
                last_error = e
                print(f"❌ Error with Gemini model {model_name} (attempt {attempt+1}): {e}")
                
                # Add a small delay before retrying
                wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                print(f"Waiting {wait_time:.1f} seconds before retry...")
                time.sleep(wait_time)
    
    # If all models and retries failed, return a helpful error message
    error_message = str(last_error) if last_error else "Unknown error"
    print(f"❌ All Gemini models failed: {error_message}")
    
    # Return a fallback message to indicate the error
    return [
        f"Error generating questions with Gemini. Please check your API key and try again.",
        f"Error details: {error_message}"
    ]

def generate_questions(ticket: Ticket) -> list[str]:
    """Main function to generate questions using Gemini"""
    return generate_questions_with_gemini(ticket)
