#!/usr/bin/env python3
"""
Migration script to add the 'edited' flag to the test_cases table.
"""
import os
import sys
import sqlite3

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.model import db_path

def migrate():
    """Add the 'edited' column to test_cases table"""
    print(f"Using database at {db_path}")
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column exists
        cursor.execute("PRAGMA table_info(test_cases)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'edited' not in columns:
            print("Adding 'edited' column to test_cases table...")
            cursor.execute("ALTER TABLE test_cases ADD COLUMN edited BOOLEAN DEFAULT 0")
            conn.commit()
            print("Column added successfully!")
        else:
            print("The 'edited' column already exists.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    if migrate():
        print("Migration completed successfully.")
    else:
        print("Migration failed!")
