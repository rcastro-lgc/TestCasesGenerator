import os
import requests
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def list_boards_and_sprints():
    auth = (JIRA_USER, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}

    # Paso 1: Obtener todos los boards
    board_url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    board_resp = requests.get(board_url, headers=headers, auth=auth)
    print("Boards response:", board_resp.status_code, board_resp.text)

    boards = board_resp.json().get("values", [])

    for board in boards:
        print(f"📋 Board: {board['name']} (ID: {board['id']})")

        # Paso 2: Obtener los sprints de ese board
        sprint_url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board['id']}/sprint"
        sprint_resp = requests.get(sprint_url, headers=headers, auth=auth)
        sprints = sprint_resp.json().get("values", [])

        for s in sprints:
            print(f"   └── 🏁 Sprint: {s['name']} (ID: {s['id']})  - Estado: {s['state']}")

if __name__ == "__main__":
    list_boards_and_sprints()
