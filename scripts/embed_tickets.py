from app.db.model import SessionLocal, Ticket
from app.db.embedding import save_embedding
from app.logic.embedder import get_embedding

def embed_all_tickets():
    session = SessionLocal()
    tickets = session.query(Ticket).all()

    for ticket in tickets:
        print(f"🧠 Embedding {ticket.jira_key}...")
        text = f"{ticket.title or ''}\n\n{ticket.description or ''}"
        vector = get_embedding(text)
        save_embedding(ticket.id, vector)

    session.close()
    print("✅ Embedding terminado.")

if __name__ == "__main__":
    embed_all_tickets()
