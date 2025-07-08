#!/usr/bin/env python3
"""
CLI tool for managing chat session database.

Usage:
    python cli_db_manager.py [command] [options]

Commands:
    stats       - Show database statistics
    search      - Search messages
    export      - Export chat data to JSON
    import      - Import chat data from JSON
    cleanup     - Clean up old chats
    backup      - Create database backup
    migrate     - Migrate from memory to SQLite
    verify      - Verify database integrity
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.config import config_service
from src.infrastructure.dependencies import get_chat_repository
from src.adapters.repositories.sqlite_chat_repository import SQLiteChatSessionRepository
from src.adapters.repositories.migration import ChatStorageMigration
from src.infrastructure.database_setup import setup_database


class DatabaseCLI:
    """Command-line interface for database management."""
    
    def __init__(self):
        self.repository = None
    
    async def initialize(self):
        """Initialize the database connection."""
        print("🔄 Initializing database connection...")
        self.repository = await setup_database()
        
        if not isinstance(self.repository, SQLiteChatSessionRepository):
            print("❌ This tool requires SQLite storage")
            print("   Set STORAGE_TYPE=sqlite in your environment")
            sys.exit(1)
    
    async def show_stats(self):
        """Show database statistics."""
        print("📊 Database Statistics")
        print("=" * 50)
        
        stats = await self.repository.get_chat_statistics()
        
        print(f"Total Chats:           {stats['total_chats']}")
        print(f"Total Messages:        {stats['total_messages']}")
        print(f"  - Bot Messages:      {stats['bot_messages']}")
        print(f"  - User Messages:     {stats['user_messages']}")
        print(f"Unique Sessions:       {stats['unique_sessions']}")
        print(f"Recent Chats (24h):    {stats['recent_chats_24h']}")
        print(f"Recent Messages (24h): {stats['recent_messages_24h']}")
        print(f"Avg Messages/Chat:     {stats['avg_messages_per_chat']}")
        
        if stats['most_active_session']['session_id']:
            print(f"Most Active Session:   {stats['most_active_session']['session_id']}")
            print(f"  - Chat Count:        {stats['most_active_session']['chat_count']}")
    
    async def search_messages(self, query: str, limit: int = 10):
        """Search messages by content."""
        print(f"🔍 Searching for: '{query}'")
        print("=" * 50)
        
        results = await self.repository.search_messages(query, limit)
        
        if not results:
            print("No messages found.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Chat: {result['chat_title']}")
            print(f"   ID: {result['chat_id']}")
            print(f"   Type: {'Bot' if result['is_bot'] else 'User'}")
            print(f"   Time: {result['timestamp']}")
            print(f"   Content: {result['content'][:100]}...")
            print()
    
    async def export_data(self, output_file: str, chat_id: str = None):
        """Export chat data to JSON file."""
        print(f"📤 Exporting data to {output_file}")
        
        chat_uuid = None
        if chat_id:
            from uuid import UUID
            try:
                chat_uuid = UUID(chat_id)
                print(f"   Exporting specific chat: {chat_id}")
            except ValueError:
                print("❌ Invalid chat ID format")
                return
        
        export_data = await self.repository.export_chat_data(chat_uuid)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Export completed:")
        print(f"   Chats exported: {export_data['total_chats']}")
        print(f"   Messages exported: {export_data['total_messages']}")
        print(f"   File: {output_file}")
    
    async def import_data(self, input_file: str):
        """Import chat data from JSON file."""
        print(f"📥 Importing data from {input_file}")
        
        if not Path(input_file).exists():
            print(f"❌ File not found: {input_file}")
            return
        
        migration = ChatStorageMigration(self.repository)
        result = await migration.import_from_json(input_file)
        
        if result['status'] == 'completed':
            print(f"✅ Import completed:")
            print(f"   Chats imported: {result['imported_count']}")
            if result['failed_count'] > 0:
                print(f"   Failed imports: {result['failed_count']}")
        else:
            print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
    
    async def cleanup_old_chats(self, days: int):
        """Clean up chats older than specified days."""
        print(f"🧹 Cleaning up chats older than {days} days...")
        
        deleted_count = await self.repository.cleanup_old_chats(days)
        print(f"✅ Deleted {deleted_count} old chats")
    
    async def create_backup(self):
        """Create a backup of the database."""
        print("💾 Creating database backup...")
        
        # Get database path
        db_path = self.repository.db_path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        
        # Copy database file
        import shutil
        shutil.copy2(db_path, backup_path)
        
        print(f"✅ Backup created: {backup_path}")
        
        # Show stats
        stats = await self.repository.get_chat_statistics()
        print(f"   Backed up {stats['total_chats']} chats with {stats['total_messages']} messages")
    
    async def verify_database(self):
        """Verify database integrity."""
        print("🔍 Verifying database integrity...")
        
        migration = ChatStorageMigration(self.repository)
        result = await migration.verify_migration()
        
        if result['status'] == 'passed':
            print("✅ Database verification passed")
        elif result['status'] == 'issues_found':
            print("⚠️  Database verification found issues:")
            for issue in result['issues']:
                print(f"   - {issue}")
        else:
            print(f"❌ Database verification failed: {result.get('error', 'Unknown error')}")
        
        # Show statistics
        if 'statistics' in result:
            stats = result['statistics']
            print(f"\nDatabase Statistics:")
            print(f"   Total chats: {stats['total_chats']}")
            print(f"   Total messages: {stats['total_messages']}")


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Chat Session Database Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search messages')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export chat data')
    export_parser.add_argument('output_file', help='Output JSON file')
    export_parser.add_argument('--chat-id', help='Specific chat ID to export')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import chat data')
    import_parser.add_argument('input_file', help='Input JSON file')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old chats')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Days old threshold')
    
    # Backup command
    subparsers.add_parser('backup', help='Create database backup')
    
    # Verify command
    subparsers.add_parser('verify', help='Verify database integrity')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = DatabaseCLI()
    await cli.initialize()
    
    # Execute command
    try:
        if args.command == 'stats':
            await cli.show_stats()
        
        elif args.command == 'search':
            await cli.search_messages(args.query, args.limit)
        
        elif args.command == 'export':
            await cli.export_data(args.output_file, args.chat_id)
        
        elif args.command == 'import':
            await cli.import_data(args.input_file)
        
        elif args.command == 'cleanup':
            await cli.cleanup_old_chats(args.days)
        
        elif args.command == 'backup':
            await cli.create_backup()
        
        elif args.command == 'verify':
            await cli.verify_database()
        
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
