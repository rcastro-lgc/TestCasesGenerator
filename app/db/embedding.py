import pickle
from app.db.model import SessionLocal, TicketEmbedding, Ticket

def save_embedding(ticket_id, vector):
    session = SessionLocal()
    obj = session.query(TicketEmbedding).filter_by(ticket_id=ticket_id).first()

    data = pickle.dumps(vector)

    if obj:
        obj.embedding = data
    else:
        obj = TicketEmbedding(ticket_id=ticket_id, embedding=data)
        session.add(obj)

    session.commit()
    session.close()

def get_all_embeddings():
    session = SessionLocal()
    all_rows = session.query(TicketEmbedding).all()
    embeddings = [(row.ticket_id, pickle.loads(row.embedding)) for row in all_rows]
    session.close()

    # Recuperar los tickets de forma segura
    session = SessionLocal()
    tickets = session.query(Ticket).filter(Ticket.id.in_([tid for tid, _ in embeddings])).all()
    ticket_map = {t.id: t for t in tickets}
    session.close()

    return [(ticket_map[tid], vec) for tid, vec in embeddings if tid in ticket_map]
