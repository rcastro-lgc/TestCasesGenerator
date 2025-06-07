import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.logic.matching import match_text_to_ticket

if len(sys.argv) < 2:
    print("⚠️  Debés pasar un archivo .txt como argumento")
    sys.exit(1)

file_path = sys.argv[1]

with open(file_path, "r", encoding="utf-8") as f:
    transcription = f.read()

matches = match_text_to_ticket(transcription, top_k=3)

print("\n🎯 Matches encontrados:")
for ticket, score in matches:
    print(f"- [{ticket.jira_key}] {ticket.title} → score: {score:.4f}")