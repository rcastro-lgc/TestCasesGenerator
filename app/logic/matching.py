from app.db.embedding import get_all_embeddings
from app.logic.embedder import get_embedding, cosine_similarity

def match_text_to_ticket(text, top_k=10):
    target_vector = get_embedding(text)
    matches = []

    for ticket, vector in get_all_embeddings():
        score = cosine_similarity(target_vector, vector)
        matches.append((ticket, score))

    matches.sort(key=lambda x: x[1], reverse=True)

    if top_k == 1:
        return matches[0]
    return matches[:top_k]
