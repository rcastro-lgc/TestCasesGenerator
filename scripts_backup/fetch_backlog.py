#!/usr/bin/env python3
"""
Script to fetch tickets from Jira using a configurable JQL query.
The JQL can be configured in two ways:
1. Using JIRA_PROJECT and JIRA_SPRINT environment variables
2. Directly setting JIRA_JQL environment variable
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from app.db.model import init_db
from app.db.save import save_or_update_ticket
from app.io.adf_parser import parse_adf_to_text

load_dotenv()

# Required Jira configuration
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not all([JIRA_BASE_URL, JIRA_USER, JIRA_API_TOKEN]):
    raise ValueError("Missing required Jira configuration. Please set JIRA_BASE_URL, JIRA_USER, and JIRA_API_TOKEN in .env")

# JQL configuration - can be set directly or constructed from project and sprint
JIRA_PROJECT = os.getenv("JIRA_PROJECT")
JIRA_SPRINT = os.getenv("JIRA_SPRINT")
JIRA_JQL = os.getenv("JIRA_JQL")

if not JIRA_JQL:
    if not all([JIRA_PROJECT, JIRA_SPRINT]):
        raise ValueError("Either JIRA_JQL or both JIRA_PROJECT and JIRA_SPRINT must be set in .env")
    JQL = f'project = {JIRA_PROJECT} AND Sprint = "{JIRA_SPRINT}" ORDER BY updated DESC'
else:
    JQL = JIRA_JQL

def fetch_backlog():
    print("🔄 Initializing database...")
    init_db()

    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (str(JIRA_USER), str(JIRA_API_TOKEN))
    params = {
        "jql": JQL,
        "fields": "summary,description,status,updated, issuetype",
        "maxResults": 150
    }

    print("📡 Querying tickets from Jira...")
    response = requests.get(url, headers=headers, params=params, auth=auth)

    issues = []
    if response.status_code == 200:
        issues = response.json().get("issues", [])
        for issue in issues:
            key = issue["key"]
            fields = issue["fields"]

            description = fields.get("description")
            if isinstance(description, dict):
                description = parse_adf_to_text(description)
            elif description is None:
                description = ""

            updated_str = fields.get("updated")
            updated_at = None
            if updated_str:
                updated_at = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%S.%f%z")

            issue_type = fields.get("issuetype", {}).get("name", "").lower()

            if issue_type == "spike":
                print(f"⏭️  Skipping SPIKE: {key}")
                continue

            ticket_data = {
                "id": key,
                "jira_key": key,
                "title": fields.get("summary"),
                "description": description,
                "issue_type": issue_type,
                "status": fields.get("status", {}).get("name", ""),
                "updated_at": updated_at
            }

            save_or_update_ticket(ticket_data)
            print(f"✅ Saved: [{key}] {fields['summary']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

    print(
        f"✅ Total tickets processed (excluding Spikes): {len([i for i in issues if i['fields'].get('issuetype', {}).get('name', '').lower() != 'spike'])}")


if __name__ == "__main__":
    fetch_backlog()
