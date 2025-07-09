# Chat Session Storage with SQLite

This document describes the SQLite-based chat session storage system that has been implemented to replace the previous in-memory storage.

## Features

### 🗃️ Persistent Storage
- **SQLite Database**: All chat sessions and messages are stored in a SQLite database
- **Automatic Schema Creation**: Database tables are created automatically on first run
- **Data Integrity**: Foreign key constraints ensure data consistency
- **Efficient Indexing**: Optimized indexes for fast queries

### 📊 Comprehensive Data Capture
The system captures extensive data about each chat session:

**Chat Sessions:**
- Unique ID (UUID)
- Title
- Session ID (for browser session tracking)
- Creation timestamp
- Last update timestamp
- Metadata (extensible JSON field)

**Messages:**
- Chat ID (foreign key)
- Content
- Bot/User flag
- Timestamp
- References (bibliographic references as JSON)
- Message order
- Metadata (extensible JSON field)

### 🔧 Administrative Features
- Database statistics and analytics
- Message search functionality
- Data export/import (JSON format)
- Automatic cleanup of old chats
- Database backup and restore
- Migration from legacy formats

## Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Database Configuration
STORAGE_TYPE=sqlite
SQLITE_PATH=data/chat_sessions.db
ENABLE_MIGRATION=true

# OpenAI Configuration (existing)
OPENAI_API_KEY=your_api_key_here
EMBEDDING_MODEL=text-embedding-3-large
COMPLETION_MODEL=gpt-4o-mini

# Milvus Configuration (existing)
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### Storage Types
- `sqlite`: Use SQLite database (recommended for production)
- `memory`: Use in-memory storage (data lost on restart)

## Database Schema

### chat_sessions table
```sql
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,           -- UUID as string
    title TEXT NOT NULL,          -- Chat title
    session_id TEXT,              -- Browser session ID
    created_at TEXT NOT NULL,     -- ISO timestamp
    updated_at TEXT NOT NULL,     -- ISO timestamp
    metadata TEXT                 -- JSON for additional data
);
```

### messages table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,        -- Foreign key to chat_sessions
    content TEXT NOT NULL,        -- Message content
    is_bot BOOLEAN NOT NULL,      -- True for bot messages
    timestamp TEXT NOT NULL,      -- ISO timestamp
    references TEXT,              -- JSON array of references
    message_order INTEGER NOT NULL, -- Order within chat
    metadata TEXT,               -- JSON for additional data
    FOREIGN KEY (chat_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
);
```

## API Endpoints

### Administrative Endpoints

All admin endpoints are prefixed with `/api/admin/`:

#### GET /api/admin/stats
Get comprehensive database statistics.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_chats": 42,
    "total_messages": 168,
    "bot_messages": 84,
    "user_messages": 84,
    "unique_sessions": 8,
    "recent_chats_24h": 5,
    "recent_messages_24h": 20,
    "avg_messages_per_chat": 4.0,
    "most_active_session": {
      "session_id": "session_1234",
      "chat_count": 12
    }
  }
}
```

#### GET /api/admin/search
Search messages by content.

**Parameters:**
- `query` (required): Search query string
- `limit` (optional): Maximum results (1-100, default 10)

**Response:**
```json
{
  "status": "success",
  "query": "peace agreement",
  "total_results": 3,
  "data": [
    {
      "message_id": 123,
      "chat_id": "uuid-here",
      "chat_title": "Peace Process Questions",
      "session_id": "session_1234",
      "content": "What was the impact of the peace agreement...",
      "is_bot": false,
      "timestamp": "2024-07-08T10:30:00Z",
      "references": null
    }
  ]
}
```

#### GET /api/admin/export
Export chat data to JSON file.

**Parameters:**
- `chat_id` (optional): Export specific chat
- `format` (optional): Export format (currently only "json")

**Returns:** File download with JSON data

#### POST /api/admin/import
Import chat data from JSON file.

**Parameters:**
- `file_path`: Path to JSON file to import

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "completed",
    "total_chats": 10,
    "imported_count": 10,
    "failed_count": 0,
    "import_timestamp": "2024-07-08T10:30:00Z"
  }
}
```

#### DELETE /api/admin/cleanup
Clean up old chats.

**Parameters:**
- `days_old` (optional): Delete chats older than N days (default 30)

**Response:**
```json
{
  "status": "success",
  "message": "Deleted 5 chats older than 30 days",
  "deleted_count": 5
}
```

#### POST /api/admin/backup
Create database backup.

**Response:**
```json
{
  "status": "success",
  "message": "Backup created successfully",
  "backup_path": "/path/to/chat_sessions.db.backup_20240708_103000",
  "backup_timestamp": "20240708_103000",
  "stats": { ... }
}
```

## Command-Line Interface

A CLI tool is provided for database management:

```bash
# Show database statistics
python cli_db_manager.py stats

# Search messages
python cli_db_manager.py search "peace agreement" --limit 5

# Export all data
python cli_db_manager.py export all_chats.json

# Export specific chat
python cli_db_manager.py export specific_chat.json --chat-id uuid-here

# Import data
python cli_db_manager.py import backup_data.json

# Clean up old chats (older than 30 days)
python cli_db_manager.py cleanup --days 30

# Create backup
python cli_db_manager.py backup

# Verify database integrity
python cli_db_manager.py verify
```

## Migration and Setup

### Automatic Setup
The database is automatically initialized when the application starts:
1. Database file and directory are created if they don't exist
2. Tables and indexes are created
3. Any legacy JSON files are automatically imported
4. Health check is performed

### Manual Migration
If you have existing chat data in JSON format:

```bash
# Import from JSON file
python cli_db_manager.py import legacy_chats.json

# Verify the import
python cli_db_manager.py verify

# Check statistics
python cli_db_manager.py stats
```

### Backup and Restore
```bash
# Create backup
python cli_db_manager.py backup

# Or manually copy the database file
cp data/chat_sessions.db data/chat_sessions.db.backup

# To restore, simply replace the database file
cp data/chat_sessions.db.backup data/chat_sessions.db
```

## Data Collected

The SQLite implementation captures comprehensive data for each chat session:

### Session Tracking
- **Session ID**: Browser session identifier for grouping chats
- **Timestamps**: Precise creation and update times
- **Chat Metadata**: Extensible JSON field for additional data

### Message Details
- **Content**: Full message text
- **Type Classification**: Bot vs User messages
- **Temporal Data**: Precise timestamps for each message
- **Order Preservation**: Messages maintain their sequence
- **References**: Complete bibliographic references with source information
- **Message Metadata**: Extensible JSON field for additional data

### Analytics Data
The system automatically tracks:
- Total conversation counts
- Message volume statistics
- Session activity patterns
- Response patterns (bot vs user ratios)
- Recent activity trends
- Most active sessions

### Searchable Content
All message content is fully searchable, enabling:
- Content analysis
- Topic discovery
- User behavior analysis
- Response quality assessment

## Performance Considerations

### Indexing Strategy
- Primary key indexes on all ID fields
- Session ID index for session-based queries
- Timestamp indexes for temporal queries
- Chat ID index for message retrieval

### Query Optimization
- Foreign key constraints with CASCADE delete
- Prepared statements for repeated queries
- Batch operations for bulk inserts
- Connection pooling for concurrent access

### Storage Efficiency
- Normalized schema to minimize data duplication
- JSON storage for flexible metadata
- Efficient data types for optimal space usage

## Security and Privacy

### Data Protection
- Local SQLite storage (no external dependencies)
- File-system level security
- No network exposure of database

### Data Retention
- Configurable cleanup policies
- Manual and automatic data purging
- Export capabilities for archival

## Troubleshooting

### Common Issues

**Database locked error:**
- Ensure no other processes are accessing the database
- Check file permissions
- Restart the application

**Migration failures:**
- Check JSON file format
- Verify file permissions
- Review error logs

**Performance issues:**
- Check database size with `stats` command
- Consider cleanup of old data
- Verify available disk space

### Maintenance

**Regular tasks:**
```bash
# Weekly statistics review
python cli_db_manager.py stats

# Monthly cleanup (adjust days as needed)
python cli_db_manager.py cleanup --days 90

# Quarterly backup
python cli_db_manager.py backup
```

**Health checks:**
```bash
# Verify database integrity
python cli_db_manager.py verify

# Search functionality test
python cli_db_manager.py search "test" --limit 1
```

This SQLite implementation provides a robust, scalable solution for chat session storage with comprehensive data capture and management capabilities.
