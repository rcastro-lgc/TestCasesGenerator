from datetime import datetime
from app.db.model import Ticket, SessionLocal

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
