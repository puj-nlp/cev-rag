"""Migration utilities for transitioning to SQLite storage."""

import json
import asyncio
from typing import Dict, List, Any
from uuid import UUID
from datetime import datetime
from pathlib import Path

from ...domain.entities import ChatSession, Message
from .sqlite_chat_repository import SQLiteChatSessionRepository
from .memory_chat_repository import InMemoryChatSessionRepository


class ChatStorageMigration:
    """Utilities for migrating chat data to SQLite."""
    
    def __init__(self, sqlite_repo: SQLiteChatSessionRepository):
        self.sqlite_repo = sqlite_repo
    
    async def migrate_from_memory(self, memory_repo: InMemoryChatSessionRepository) -> Dict[str, Any]:
        """Migrate data from in-memory storage to SQLite."""
        print("Starting migration from memory storage to SQLite...")
        
        chats = await memory_repo.find_all()
        migrated_count = 0
        failed_count = 0
        failed_chats = []
        
        for chat in chats:
            try:
                await self.sqlite_repo.save(chat)
                migrated_count += 1
                print(f"✅ Migrated chat: {chat.title} ({chat.id})")
            except Exception as e:
                failed_count += 1
                failed_chats.append({
                    'chat_id': str(chat.id),
                    'title': chat.title,
                    'error': str(e)
                })
                print(f"❌ Failed to migrate chat: {chat.title} ({chat.id}) - {e}")
        
        result = {
            'status': 'completed',
            'total_chats': len(chats),
            'migrated_count': migrated_count,
            'failed_count': failed_count,
            'failed_chats': failed_chats,
            'migration_timestamp': datetime.now().isoformat()
        }
        
        print(f"\nMigration completed: {migrated_count}/{len(chats)} chats migrated successfully")
        if failed_count > 0:
            print(f"Failed migrations: {failed_count}")
        
        return result
    
    async def import_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """Import chat data from a JSON file."""
        print(f"Importing chat data from {json_file_path}...")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            failed_count = 0
            failed_imports = []
            
            chats_data = data.get('chats', [])
            
            for chat_data in chats_data:
                try:
                    # Convert messages
                    messages = []
                    for msg_data in chat_data.get('messages', []):
                        message = Message(
                            content=msg_data['content'],
                            is_bot=msg_data.get('is_bot', False),
                            timestamp=datetime.fromisoformat(msg_data['timestamp']) if msg_data.get('timestamp') else datetime.now(),
                            references=msg_data.get('references')
                        )
                        messages.append(message)
                    
                    # Create chat session
                    chat_session = ChatSession(
                        id=UUID(chat_data['id']),
                        title=chat_data['title'],
                        session_id=chat_data.get('session_id'),
                        messages=messages,
                        created_at=datetime.fromisoformat(chat_data['created_at']),
                        updated_at=datetime.fromisoformat(chat_data['updated_at'])
                    )
                    
                    await self.sqlite_repo.save(chat_session)
                    imported_count += 1
                    print(f"✅ Imported chat: {chat_session.title} ({chat_session.id})")
                    
                except Exception as e:
                    failed_count += 1
                    failed_imports.append({
                        'chat_data': chat_data.get('title', 'Unknown'),
                        'error': str(e)
                    })
                    print(f"❌ Failed to import chat: {e}")
            
            result = {
                'status': 'completed',
                'total_chats': len(chats_data),
                'imported_count': imported_count,
                'failed_count': failed_count,
                'failed_imports': failed_imports,
                'import_timestamp': datetime.now().isoformat()
            }
            
            print(f"\nImport completed: {imported_count}/{len(chats_data)} chats imported successfully")
            return result
            
        except Exception as e:
            print(f"❌ Failed to import from JSON: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'import_timestamp': datetime.now().isoformat()
            }
    
    async def export_to_json(self, output_file_path: str, chat_id: UUID = None) -> Dict[str, Any]:
        """Export chat data to a JSON file."""
        print(f"Exporting chat data to {output_file_path}...")
        
        try:
            export_data = await self.sqlite_repo.export_chat_data(chat_id)
            
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Export completed: {export_data['total_chats']} chats exported")
            return {
                'status': 'completed',
                'file_path': output_file_path,
                'total_chats': export_data['total_chats'],
                'total_messages': export_data['total_messages'],
                'export_timestamp': export_data['export_timestamp']
            }
            
        except Exception as e:
            print(f"❌ Failed to export to JSON: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'export_timestamp': datetime.now().isoformat()
            }
    
    async def verify_migration(self) -> Dict[str, Any]:
        """Verify the integrity of migrated data."""
        print("Verifying migration integrity...")
        
        try:
            stats = await self.sqlite_repo.get_chat_statistics()
            
            # Check for potential issues
            issues = []
            
            if stats['total_chats'] == 0:
                issues.append("No chats found in database")
            
            if stats['total_messages'] == 0:
                issues.append("No messages found in database")
            
            if stats['avg_messages_per_chat'] == 0:
                issues.append("Average messages per chat is 0")
            
            # Check for orphaned messages (shouldn't happen with foreign keys)
            
            verification_result = {
                'status': 'passed' if not issues else 'issues_found',
                'statistics': stats,
                'issues': issues,
                'verification_timestamp': datetime.now().isoformat()
            }
            
            if not issues:
                print("✅ Migration verification passed")
            else:
                print("⚠️ Migration verification found issues:")
                for issue in issues:
                    print(f"  - {issue}")
            
            return verification_result
            
        except Exception as e:
            print(f"❌ Migration verification failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'verification_timestamp': datetime.now().isoformat()
            }


async def run_migration_script():
    """Standalone migration script."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migration.py [migrate|import|export|verify] [options]")
        print("Commands:")
        print("  migrate - Migrate from memory to SQLite")
        print("  import <json_file> - Import from JSON file")
        print("  export <json_file> [chat_id] - Export to JSON file")
        print("  verify - Verify migration integrity")
        return
    
    command = sys.argv[1]
    sqlite_repo = SQLiteChatSessionRepository("chat_sessions.db")
    migration = ChatStorageMigration(sqlite_repo)
    
    if command == "migrate":
        memory_repo = InMemoryChatSessionRepository()
        result = await migration.migrate_from_memory(memory_repo)
        print(json.dumps(result, indent=2))
    
    elif command == "import" and len(sys.argv) >= 3:
        json_file = sys.argv[2]
        result = await migration.import_from_json(json_file)
        print(json.dumps(result, indent=2))
    
    elif command == "export" and len(sys.argv) >= 3:
        json_file = sys.argv[2]
        chat_id = UUID(sys.argv[3]) if len(sys.argv) >= 4 else None
        result = await migration.export_to_json(json_file, chat_id)
        print(json.dumps(result, indent=2))
    
    elif command == "verify":
        result = await migration.verify_migration()
        print(json.dumps(result, indent=2))
    
    else:
        print("Invalid command or missing arguments")


if __name__ == "__main__":
    asyncio.run(run_migration_script())
