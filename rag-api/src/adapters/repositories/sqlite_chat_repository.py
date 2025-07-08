"""SQLite implementation of ChatSessionRepository."""

import sqlite3
import json
import asyncio
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime
from pathlib import Path

from ...domain.entities import ChatSession, Message
from ...domain.ports import ChatSessionRepository


class SQLiteChatSessionRepository(ChatSessionRepository):
    """SQLite implementation of chat session repository."""
    
    def __init__(self, db_path: str = "chat_sessions.db"):
        """Initialize the SQLite repository.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create the database and tables if they don't exist."""
        try:
            print(f"Creating SQLite database at: {self.db_path}")
            
            # Ensure parent directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
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
                
                # Create indexes for better performance
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
                
                conn.commit()
                
        except Exception as e:
            print(f"Error creating database: {e}")
            raise
    
    def _chat_session_from_row(self, row: sqlite3.Row, messages: List[Message] = None) -> ChatSession:
        """Convert a database row to a ChatSession entity."""
        return ChatSession(
            id=UUID(row['id']),
            title=row['title'],
            session_id=row['session_id'],
            messages=messages or [],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def _message_from_row(self, row: sqlite3.Row) -> Message:
        """Convert a database row to a Message entity."""
        references = None
        if row['message_references']:
            try:
                references = json.loads(row['message_references'])
            except (json.JSONDecodeError, TypeError):
                references = None
        
        return Message(
            content=row['content'],
            is_bot=bool(row['is_bot']),
            timestamp=datetime.fromisoformat(row['timestamp']),
            references=references
        )
    
    async def save(self, chat_session: ChatSession) -> ChatSession:
        """Save a chat session with all its messages."""
        def _save_sync():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Save or update chat session
                conn.execute('''
                    INSERT OR REPLACE INTO chat_sessions 
                    (id, title, session_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    str(chat_session.id),
                    chat_session.title,
                    chat_session.session_id,
                    chat_session.created_at.isoformat(),
                    chat_session.updated_at.isoformat()
                ))
                
                # Delete existing messages for this chat
                conn.execute('DELETE FROM messages WHERE chat_id = ?', (str(chat_session.id),))
                
                # Save all messages
                for i, message in enumerate(chat_session.messages):
                    references_json = None
                    if message.references:
                        try:
                            references_json = json.dumps(message.references)
                        except (TypeError, ValueError):
                            references_json = None
                    
                    conn.execute('''
                        INSERT INTO messages 
                        (chat_id, content, is_bot, timestamp, message_references, message_order)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        str(chat_session.id),
                        message.content,
                        message.is_bot,
                        message.timestamp.isoformat() if message.timestamp else datetime.now().isoformat(),
                        references_json,
                        i
                    ))
                
                conn.commit()
        
        # Run in thread to avoid blocking
        await asyncio.get_event_loop().run_in_executor(None, _save_sync)
        return chat_session
    
    async def find_by_id(self, chat_id: UUID) -> Optional[ChatSession]:
        """Find a chat session by ID with all its messages."""
        def _find_sync():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get chat session
                chat_cursor = conn.execute(
                    'SELECT * FROM chat_sessions WHERE id = ?', 
                    (str(chat_id),)
                )
                chat_row = chat_cursor.fetchone()
                
                if not chat_row:
                    return None
                
                # Get messages ordered by message_order
                messages_cursor = conn.execute('''
                    SELECT * FROM messages 
                    WHERE chat_id = ? 
                    ORDER BY message_order, timestamp
                ''', (str(chat_id),))
                
                messages = [self._message_from_row(row) for row in messages_cursor.fetchall()]
                
                return self._chat_session_from_row(chat_row, messages)
        
        return await asyncio.get_event_loop().run_in_executor(None, _find_sync)
    
    async def find_all(self) -> List[ChatSession]:
        """Find all chat sessions (without messages for performance)."""
        def _find_all_sync():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT * FROM chat_sessions 
                    ORDER BY updated_at DESC
                ''')
                
                return [self._chat_session_from_row(row) for row in cursor.fetchall()]
        
        return await asyncio.get_event_loop().run_in_executor(None, _find_all_sync)
    
    async def find_by_session_id(self, session_id: str) -> List[ChatSession]:
        """Find all chat sessions for a specific session ID."""
        def _find_by_session_sync():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT * FROM chat_sessions 
                    WHERE session_id = ? 
                    ORDER BY updated_at DESC
                ''', (session_id,))
                
                return [self._chat_session_from_row(row) for row in cursor.fetchall()]
        
        return await asyncio.get_event_loop().run_in_executor(None, _find_by_session_sync)
    
    async def delete(self, chat_id: UUID) -> bool:
        """Delete a chat session and all its messages."""
        def _delete_sync():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'DELETE FROM chat_sessions WHERE id = ?', 
                    (str(chat_id),)
                )
                conn.commit()
                return cursor.rowcount > 0
        
        return await asyncio.get_event_loop().run_in_executor(None, _delete_sync)
    
    async def get_chat_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about stored chats."""
        def _get_stats_sync():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Total chats and messages
                total_chats = conn.execute('SELECT COUNT(*) as count FROM chat_sessions').fetchone()['count']
                total_messages = conn.execute('SELECT COUNT(*) as count FROM messages').fetchone()['count']
                
                # Messages by type
                bot_messages = conn.execute('SELECT COUNT(*) as count FROM messages WHERE is_bot = 1').fetchone()['count']
                user_messages = conn.execute('SELECT COUNT(*) as count FROM messages WHERE is_bot = 0').fetchone()['count']
                
                # Sessions with activity
                unique_sessions = conn.execute('SELECT COUNT(DISTINCT session_id) as count FROM chat_sessions WHERE session_id IS NOT NULL').fetchone()['count']
                
                # Recent activity (last 24 hours)
                recent_chats = conn.execute('''
                    SELECT COUNT(*) as count FROM chat_sessions 
                    WHERE datetime(created_at) > datetime('now', '-1 day')
                ''').fetchone()['count']
                
                recent_messages = conn.execute('''
                    SELECT COUNT(*) as count FROM messages 
                    WHERE datetime(timestamp) > datetime('now', '-1 day')
                ''').fetchone()['count']
                
                # Average messages per chat
                avg_messages = total_messages / total_chats if total_chats > 0 else 0
                
                # Most active session
                most_active_session = conn.execute('''
                    SELECT session_id, COUNT(*) as chat_count
                    FROM chat_sessions 
                    WHERE session_id IS NOT NULL
                    GROUP BY session_id
                    ORDER BY chat_count DESC
                    LIMIT 1
                ''').fetchone()
                
                return {
                    'total_chats': total_chats,
                    'total_messages': total_messages,
                    'bot_messages': bot_messages,
                    'user_messages': user_messages,
                    'unique_sessions': unique_sessions,
                    'recent_chats_24h': recent_chats,
                    'recent_messages_24h': recent_messages,
                    'avg_messages_per_chat': round(avg_messages, 2),
                    'most_active_session': {
                        'session_id': most_active_session['session_id'] if most_active_session else None,
                        'chat_count': most_active_session['chat_count'] if most_active_session else 0
                    }
                }
        
        return await asyncio.get_event_loop().run_in_executor(None, _get_stats_sync)
    
    async def search_messages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search messages by content."""
        def _search_sync():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT m.*, cs.title as chat_title, cs.session_id
                    FROM messages m
                    JOIN chat_sessions cs ON m.chat_id = cs.id
                    WHERE m.content LIKE ?
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                ''', (f'%{query}%', limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'message_id': row['id'],
                        'chat_id': row['chat_id'],
                        'chat_title': row['chat_title'],
                        'session_id': row['session_id'],
                        'content': row['content'],
                        'is_bot': bool(row['is_bot']),
                        'timestamp': row['timestamp'],
                        'references': json.loads(row['message_references']) if row['message_references'] else None
                    })
                
                return results
        
        return await asyncio.get_event_loop().run_in_executor(None, _search_sync)
    
    async def export_chat_data(self, chat_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Export chat data for backup or analysis."""
        def _export_sync():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if chat_id:
                    # Export specific chat
                    chat_cursor = conn.execute('SELECT * FROM chat_sessions WHERE id = ?', (str(chat_id),))
                    chats = chat_cursor.fetchall()
                    
                    messages_cursor = conn.execute('SELECT * FROM messages WHERE chat_id = ? ORDER BY message_order', (str(chat_id),))
                    messages = messages_cursor.fetchall()
                else:
                    # Export all chats
                    chat_cursor = conn.execute('SELECT * FROM chat_sessions ORDER BY created_at')
                    chats = chat_cursor.fetchall()
                    
                    messages_cursor = conn.execute('SELECT * FROM messages ORDER BY chat_id, message_order')
                    messages = messages_cursor.fetchall()
                
                # Convert to dictionaries
                chats_data = []
                for chat in chats:
                    chat_dict = dict(chat)
                    chat_messages = [dict(msg) for msg in messages if msg['chat_id'] == chat['id']]
                    chat_dict['messages'] = chat_messages
                    chats_data.append(chat_dict)
                
                return {
                    'export_timestamp': datetime.now().isoformat(),
                    'chat_id': str(chat_id) if chat_id else None,
                    'total_chats': len(chats_data),
                    'total_messages': len(messages),
                    'chats': chats_data
                }
        
        return await asyncio.get_event_loop().run_in_executor(None, _export_sync)
    
    async def cleanup_old_chats(self, days_old: int = 30) -> int:
        """Delete chats older than specified days."""
        def _cleanup_sync():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM chat_sessions 
                    WHERE datetime(updated_at) < datetime('now', '-{} days')
                '''.format(days_old))
                conn.commit()
                return cursor.rowcount
        
        return await asyncio.get_event_loop().run_in_executor(None, _cleanup_sync)
