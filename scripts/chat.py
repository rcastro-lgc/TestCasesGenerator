#!/usr/bin/env python3
"""
Intelligent chatbot for querying Jira ticket information.
Uses GPT to analyze and answer questions based on tickets.
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.logic.matching import match_text_to_ticket
from app.logic.embedder import get_embedding
from app.db.model import SessionLocal, Ticket

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_ticket_for_context(ticket, score=None):
    """Format a ticket for use as context in the prompt."""
    relevance = f"{score:.2%}" if score is not None else "N/A"
    return f"""
Ticket: {ticket.jira_key}
Title: {ticket.title}
Type: {ticket.issue_type}
Status: {ticket.status}
Description: {ticket.description}
Relevance: {relevance}
"""

def generate_response(question: str, relevant_tickets: list) -> str:
    """Generate a coherent response using GPT."""
    # Prepare context with relevant tickets
    context = "\n".join(format_ticket_for_context(ticket, score) for ticket, score in relevant_tickets)
    
    prompt = f"""You are an expert assistant for the project. Your task is to answer questions based on Jira ticket information.

Context (relevant tickets):
{context}

Question: {question}

Instructions:
1. Analyze the ticket information
2. Provide a clear and concise response
3. If information is insufficient, indicate it
4. Include references to relevant tickets (using their ticket keys)
5. If there are contradictions or ambiguities, mention them
6. IMPORTANT: Respond in the SAME LANGUAGE as the question. If the question is in Spanish, respond in Spanish. If in English, respond in English.

Response:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

def chat():
    print("\n🤖 Intelligent Ticket Assistant")
    print("=" * 50)
    print("You can ask about any aspect of the project.")
    print("Examples:")
    print("- What authentication features are we working on?")
    print("- What are the main bugs we need to fix?")
    print("- What features are in development?")
    print("- Show me tickets related to user management")
    print("=" * 50)
    
    while True:
        try:
            # Get user question
            question = input("\n❓ Your question (or 'exit' to quit): ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            # Find relevant tickets
            matches = match_text_to_ticket(question, top_k=5)
            
            if not matches:
                print("\n❌ No relevant information found for your question.")
                continue
            
            # Generate and show response
            print("\n🤔 Analyzing information...")
            response = generate_response(question, matches)
            print("\n📚 Response:")
            print(response)
            
            # Show references
            print("\n📋 Ticket References:")
            for ticket, score in matches:
                print(f"- {ticket.jira_key}: {ticket.title} (Relevance: {score:.2%})")
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    chat() 