"""Database initialization and migration utilities."""

import os
import asyncio
from pathlib import Path

from ..infrastructure.config import config_service
from ..infrastructure.dependencies import get_chat_repository
from ..adapters.repositories.sqlite_chat_repository import SQLiteChatSessionRepository
from ..adapters.repositories.memory_chat_repository import InMemoryChatSessionRepository
from ..adapters.repositories.migration import ChatStorageMigration


async def initialize_database():
    """Initialize the database and perform migrations if needed."""
    print("🔄 Initializing database...")
    
    database_config = config_service.database
    
    # Ensure data directory exists
    if database_config.storage_type == "sqlite":
        db_path = Path(database_config.sqlite_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"📁 Database directory: {db_path.parent}")
        print(f"🗃️  Database file: {db_path}")
    
    # Get repository instance (this will create the database if using SQLite)
    repository = get_chat_repository()
    
    if isinstance(repository, SQLiteChatSessionRepository):
        print("✅ SQLite database initialized successfully")
        
        # Get initial statistics
        try:
            stats = await repository.get_chat_statistics()
            print(f"📊 Database stats: {stats['total_chats']} chats, {stats['total_messages']} messages")
        except Exception as e:
            print(f"⚠️  Could not retrieve statistics: {e}")
    
    elif isinstance(repository, InMemoryChatSessionRepository):
        print("✅ In-memory storage initialized")
        print("⚠️  Note: Chat data will not persist between restarts")
    
    return repository


async def migrate_from_memory_if_needed():
    """Migrate from memory storage to SQLite if enabled and needed."""
    database_config = config_service.database
    
    if not database_config.enable_migration or database_config.storage_type != "sqlite":
        return
    
    # Check if there's a legacy data file or memory state to migrate
    legacy_files = [
        "chats.json",
        "chat_sessions.json",
        "legacy_chats.json"
    ]
    
    sqlite_repo = get_chat_repository()
    if not isinstance(sqlite_repo, SQLiteChatSessionRepository):
        return
    
    migration = ChatStorageMigration(sqlite_repo)
    
    # Check for JSON files to import
    for legacy_file in legacy_files:
        if os.path.exists(legacy_file):
            print(f"🔄 Found legacy data file: {legacy_file}")
            try:
                result = await migration.import_from_json(legacy_file)
                if result['status'] == 'completed':
                    print(f"✅ Successfully imported {result['imported_count']} chats from {legacy_file}")
                    
                    # Rename the file to prevent re-import
                    backup_name = f"{legacy_file}.imported"
                    os.rename(legacy_file, backup_name)
                    print(f"📦 Legacy file backed up as {backup_name}")
                else:
                    print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Error importing {legacy_file}: {e}")


async def perform_database_health_check():
    """Perform a health check on the database."""
    print("🔍 Performing database health check...")
    
    repository = get_chat_repository()
    
    try:
        if isinstance(repository, SQLiteChatSessionRepository):
            # Test basic operations
            stats = await repository.get_chat_statistics()
            print(f"✅ Database connection: OK")
            print(f"📊 Total chats: {stats['total_chats']}")
            print(f"💬 Total messages: {stats['total_messages']}")
            print(f"👥 Unique sessions: {stats['unique_sessions']}")
            
            if stats['total_chats'] > 0:
                # Test reading a chat
                chats = await repository.find_all()
                if chats:
                    test_chat = await repository.find_by_id(chats[0].id)
                    if test_chat:
                        print(f"✅ Chat retrieval: OK")
                    else:
                        print(f"⚠️  Chat retrieval: Failed")
        
        elif isinstance(repository, InMemoryChatSessionRepository):
            # Test memory storage
            chats = await repository.find_all()
            print(f"✅ In-memory storage: OK ({len(chats)} chats)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False


async def setup_database():
    """Complete database setup process."""
    print("🚀 Starting database setup...")
    
    try:
        # Initialize database
        repository = await initialize_database()
        
        # Perform migration if needed
        await migrate_from_memory_if_needed()
        
        # Health check
        health_ok = await perform_database_health_check()
        
        if health_ok:
            print("✅ Database setup completed successfully!")
        else:
            print("⚠️  Database setup completed with warnings")
        
        return repository
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        raise


if __name__ == "__main__":
    # Allow running this script directly for database management
    asyncio.run(setup_database())
