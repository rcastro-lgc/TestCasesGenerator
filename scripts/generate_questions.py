import os
from app.db.model import SessionLocal, Ticket
from app.logic.question_generator import generate_questions

# Output path
output_path = os.path.abspath("../data/questions/questions_by_ticket.md")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Get tickets that haven't been processed yet
session = SessionLocal()
tickets = session.query(Ticket).filter(
    Ticket.issue_type != "Spike",
    Ticket.questions_generated != True
).all()

with open(output_path, "w", encoding="utf-8") as f:
    for idx, ticket in enumerate(tickets):
        print(f"🔄 Generating questions for {ticket.jira_key} ({idx+1}/{len(tickets)})")
        questions = generate_questions(ticket)

        f.write(f"## {ticket.jira_key} - {ticket.title.strip() if ticket.title is not None else ''}\n")
        f.write(f"**Type:** {ticket.issue_type}\n\n")

        if questions:
            f.write("**Generated questions:**\n")
            for q in questions:
                f.write(f"- {q}\n")
            # Mark ticket as processed
            setattr(ticket, "questions_generated", True)  # Set the instance attribute, not the Column object
            session.add(ticket)
        else:
            f.write("_No questions generated._\n")

        f.write("\n---\n\n")

session.commit()
session.close()
print(f"✅ Questions generated and saved to: {output_path}")
