"""
Script to create sample test data for testing the database implementation.
"""

import os
import sys
import uuid
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.model import init_db, SessionLocal, Ticket, TestCase
from app.db.save import save_test_case

def create_sample_data():
    print("Creating sample test data...")
    
    # Initialize database
    init_db()
    
    # Create a sample ticket if none exists
    session = SessionLocal()
    ticket = session.query(Ticket).first()
    
    if not ticket:
        # Create a sample ticket
        ticket_id = str(uuid.uuid4())
        ticket = Ticket(
            id=ticket_id,
            jira_key="SAMPLE-123",
            title="Sample Ticket for Testing",
            description="This is a sample ticket description for testing the test case database implementation.",
            status="Open",
            issue_type="Task",
            updated_at=datetime.utcnow(),
            fetched_at=datetime.utcnow(),
            questions_generated=False,
            test_cases_generated=False
        )
        session.add(ticket)
        session.commit()
        print(f"Created sample ticket: {ticket.jira_key}")
    else:
        print(f"Using existing ticket: {ticket.jira_key}")
    
    # Create some sample test cases
    for i in range(1, 4):
        test_case = save_test_case(
            ticket_id=ticket.id,
            scenario=f"Sample scenario {i} for testing",
            action=f"User performs action {i}",
            expected_behavior=f"The system should respond with expected behavior {i}"
        )
        print(f"Created test case {i} for ticket {ticket.jira_key}")
    
    session.close()
    print("Sample data creation completed.")

if __name__ == "__main__":
    create_sample_data()
