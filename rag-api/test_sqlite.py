#!/usr/bin/env python3
"""Test script to debug SQLite repository issues."""

import sys
import os
import sqlite3
import tempfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, '/home/satoru/repos/u/Version_4_Upload/rag-api')

def test_sqlite_schema():
    """Test the SQLite schema creation."""
    print("Testing SQLite schema creation...")
    
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        print(f"Using database: {db_path}")
        
        with sqlite3.connect(db_path) as conn:
            print("Connected to database")
            
            conn.execute("PRAGMA foreign_keys = ON")
            print("Foreign keys enabled")
            
            # Create chat_sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            print("Created chat_sessions table")
            
            # Create messages table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    is_bot BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    message_references TEXT,
                    message_order INTEGER NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (chat_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
                )
            ''')
            print("Created messages table")
            
            # Create indexes
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id 
                ON chat_sessions (session_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_chat_id 
                ON messages (chat_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                ON messages (timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at 
                ON chat_sessions (created_at)
            ''')
            print("Created indexes")
            
            conn.commit()
            print("Schema creation successful!")
            
            # Test a simple insert
            conn.execute('''
                INSERT INTO chat_sessions (id, title, session_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', ('test-id', 'Test Chat', 'test-session', '2024-07-08T10:30:00Z', '2024-07-08T10:30:00Z'))
            
            conn.execute('''
                INSERT INTO messages (chat_id, content, is_bot, timestamp, message_references, message_order)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('test-id', 'Test message', False, '2024-07-08T10:30:00Z', None, 0))
            
            conn.commit()
            print("Test data inserted successfully!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)
            print(f"Cleaned up {db_path}")


def test_repository_import():
    """Test importing the SQLite repository."""
    print("Testing repository import...")
    
    try:
        from src.adapters.repositories.sqlite_chat_repository import SQLiteChatSessionRepository
        print("SQLiteChatSessionRepository imported successfully")
        
        # Test creating an instance
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            repo = SQLiteChatSessionRepository(db_path)
            print("Repository created successfully")
        except Exception as e:
            print(f"Error creating repository: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
                
    except Exception as e:
        print(f"Error importing repository: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting SQLite debug tests...\n")
    
    test_sqlite_schema()
    print()
    test_repository_import()
