"""
Migration script to create the test_cases table.
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.model import init_db, Base, engine, TestCase, Ticket

def run_migration():
    print("Starting database migration for test cases...")
    
    # Create tables that don't exist yet
    Base.metadata.create_all(engine)
    
    print("Migration completed successfully.")

if __name__ == "__main__":
    run_migration()
