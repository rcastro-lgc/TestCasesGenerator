from datetime import datetime
from app.db.model import Ticket, TestCase, SessionLocal
import uuid

def save_or_update_ticket(ticket_data):
    session = SessionLocal()
    existing = session.query(Ticket).filter_by(jira_key=ticket_data['jira_key']).first()

    if existing:
        incoming_updated = ticket_data['updated_at']
        local_updated = existing.updated_at

        # Eliminar tzinfo para comparación limpia (ambos sin zona)
        if incoming_updated and local_updated:
            if incoming_updated.replace(tzinfo=None) > local_updated.replace(tzinfo=None):
                for k, v in ticket_data.items():
                    setattr(existing, k, v)
                existing.fetched_at = datetime.utcnow()
                existing.questions_generated = False  # resetear preguntas
        else:
            # fallback si alguno es None
            for k, v in ticket_data.items():
                setattr(existing, k, v)
            existing.fetched_at = datetime.utcnow()
            existing.questions_generated = False
    else:
        ticket = Ticket(**ticket_data, fetched_at=datetime.utcnow(), questions_generated=False)
        session.add(ticket)

    session.commit()
    session.close()

def save_test_case(ticket_id, scenario, action, expected_behavior):
    """
    Save a test case to the database.
    
    Args:
        ticket_id: The ID of the ticket that this test case belongs to
        scenario: The test scenario description
        action: The action to perform in the test
        expected_behavior: The expected behavior or outcome
    
    Returns:
        The created TestCase object
    """
    session = SessionLocal()
    
    test_case = TestCase(
        id=str(uuid.uuid4()),
        ticket_id=ticket_id,
        scenario=scenario,
        action=action,
        expected_behavior=expected_behavior,
        created_at=datetime.utcnow()
    )
    
    session.add(test_case)
    session.commit()
    
    session.refresh(test_case)
    session.close()
    
    return test_case
