#!/usr/bin/env python3
"""
Script to check or update the posted_to_jira status for tickets.

Usage:
  python test_jira_status.py show [ticket_id]        # Show status for all tickets or a specific one
  python test_jira_status.py set [ticket_id] [0|1]   # Set status for a specific ticket (0=False, 1=True)
"""

import os
import sys
import sqlite3
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).resolve().parent.parent
db_path = project_root / "data" / "FuzeTestAI.db"

def connect_db():
    """Connect to the SQLite database."""
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        sys.exit(1)
    return sqlite3.connect(db_path)

def show_status(ticket_id=None):
    """Show posted_to_jira status for all tickets or a specific one."""
    conn = connect_db()
    cursor = conn.cursor()
    
    if ticket_id:
        cursor.execute(
            "SELECT jira_key, title, posted_to_jira FROM tickets WHERE jira_key = ?", 
            (ticket_id,)
        )
        row = cursor.fetchone()
        if row:
            print(f"Ticket {row[0]} - {row[1]}")
            print(f"  posted_to_jira: {bool(row[2])}")
        else:
            print(f"Ticket {ticket_id} not found")
    else:
        cursor.execute(
            "SELECT jira_key, title, posted_to_jira FROM tickets ORDER BY jira_key"
        )
        rows = cursor.fetchall()
        print(f"Found {len(rows)} tickets:")
        for row in rows:
            print(f"Ticket {row[0]} - {row[1]}")
            print(f"  posted_to_jira: {bool(row[2])}")
            print()
    
    conn.close()

def set_status(ticket_id, status):
    """Set posted_to_jira status for a specific ticket."""
    if ticket_id is None:
        print("Please provide a ticket ID")
        sys.exit(1)
    
    status_value = bool(int(status))
    conn = connect_db()
    cursor = conn.cursor()
    
    # First check if the ticket exists
    cursor.execute("SELECT id FROM tickets WHERE jira_key = ?", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        print(f"Ticket {ticket_id} not found")
        conn.close()
        sys.exit(1)
    
    # Update the status
    cursor.execute(
        "UPDATE tickets SET posted_to_jira = ? WHERE jira_key = ?", 
        (status_value, ticket_id)
    )
    conn.commit()
    
    print(f"Updated ticket {ticket_id} posted_to_jira status to {status_value}")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "show":
        ticket_id = sys.argv[2] if len(sys.argv) > 2 else None
        show_status(ticket_id)
    elif command == "set":
        if len(sys.argv) < 4:
            print("Missing ticket_id or status value")
            print(__doc__)
            sys.exit(1)
        ticket_id = sys.argv[2]
        status = sys.argv[3]
        set_status(ticket_id, status)
    else:
        print("Unknown command:", command)
        print(__doc__)
        sys.exit(1)
