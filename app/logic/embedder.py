import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

EMBEDDING_DIMENSION = 768  # Default embedding dimension for Google's text-embedding

def get_embedding(text: str) -> list:
    if not text.strip():
        return [0.0] * EMBEDDING_DIMENSION

    # Truncate if too long (based on character count)
    if len(text) > 30000:
        text = text[:30000]

    try:
        # Use Google's embedding model
        model = genai.get_embeddings_model()
        response = model.embed_content(
            content=text.strip(),
            task_type="RETRIEVAL_QUERY"
        )
        return response.embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return [0.0] * EMBEDDING_DIMENSION

def cosine_similarity(vec1: list, vec2: list) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
