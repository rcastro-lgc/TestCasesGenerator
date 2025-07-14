from app.db.model import SessionLocal, Ticket
from app.logic.test_case_generator import generate_test_cases
from app.db.save import save_test_case
import os

# Get all valid tickets
session = SessionLocal()
tickets = session.query(Ticket).filter(
    Ticket.test_cases_generated == False,
    Ticket.description != None,
    Ticket.title != None
).all()
session.close()

total_tickets = len(tickets)
tickets_processed = 0
total_test_cases = 0

for idx, ticket in enumerate(tickets, 1):
    print(f"🧪 Generating test cases for {ticket.jira_key} ({idx}/{total_tickets})")
    test_cases = generate_test_cases(ticket)

    if test_cases:
        current_block = []
        test_case_count = 0

        for line in test_cases:
            line = line.strip()
            if not line:
                continue

            current_block.append(line)

            if len(current_block) == 3:
                scenario = action = expected = "(not detected)"

                for item in current_block:
                    lower = item.lower().replace("**", "").replace("-", "").strip()
                    if lower.startswith("scenario"):
                        scenario = item.split(":", 1)[-1].strip()
                    elif lower.startswith("action"):
                        action = item.split(":", 1)[-1].strip()
                    elif "expected behavior" in lower:
                        expected = item.split(":", 1)[-1].strip()

                test_case_count += 1
                total_test_cases += 1

                # Save test case to database
                try:
                    save_test_case(ticket.id, scenario, action, expected)
                    print(f"✅ Test case saved to database for ticket {ticket.jira_key}")
                except Exception as e:
                    print(f"❌ Error saving test case to database: {str(e)}")

                current_block = []

        if test_case_count > 0:
            tickets_processed += 1
            session = SessionLocal()
            db_ticket = session.query(Ticket).filter_by(jira_key=ticket.jira_key).first()
            if db_ticket is not None:
                setattr(db_ticket, "test_cases_generated", True)  # Set the instance attribute, not the Column object
                session.commit()
                print(f"✅ Generated {test_case_count} test cases for ticket {ticket.jira_key}")
            else:
                print(f"❌ Ticket with jira_key {ticket.jira_key} not found in database.")
            session.close()
        else:
            print(f"⚠️ No valid test cases detected for ticket {ticket.jira_key}")
    else:
        print(f"⚠️ No test cases generated for ticket {ticket.jira_key}")

print(f"✅ Test cases generation completed: {total_test_cases} test cases for {tickets_processed} tickets")
