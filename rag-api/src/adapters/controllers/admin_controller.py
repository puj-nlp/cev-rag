"""Admin controller for database management and statistics."""

from typing import Dict, Any, Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
import tempfile
import os
import json

from ...infrastructure.dependencies import get_chat_repository
from ...adapters.repositories.sqlite_chat_repository import SQLiteChatSessionRepository
from ...adapters.repositories.migration import ChatStorageMigration


class AdminController:
    """Controller for administrative operations."""
    
    def __init__(self):
        self.router = APIRouter(prefix="/admin", tags=["admin"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the routes for this controller."""
        self.router.add_api_route(
            "/stats",
            self.get_statistics,
            methods=["GET"],
            response_model=Dict[str, Any]
        )
        self.router.add_api_route(
            "/search",
            self.search_messages,
            methods=["GET"],
            response_model=List[Dict[str, Any]]
        )
        self.router.add_api_route(
            "/export",
            self.export_data,
            methods=["GET"],
            response_class=FileResponse
        )
        self.router.add_api_route(
            "/import",
            self.import_data,
            methods=["POST"]
        )
        self.router.add_api_route(
            "/cleanup",
            self.cleanup_old_chats,
            methods=["DELETE"]
        )
        self.router.add_api_route(
            "/backup",
            self.create_backup,
            methods=["POST"]
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        repository = get_chat_repository()
        
        if not isinstance(repository, SQLiteChatSessionRepository):
            raise HTTPException(
                status_code=501, 
                detail="Statistics only available for SQLite storage"
            )
        
        try:
            stats = await repository.get_chat_statistics()
            return {
                "status": "success",
                "data": stats
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")
    
    async def search_messages(
        self,
        query: str = Query(..., description="Search query for message content"),
        limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
    ) -> List[Dict[str, Any]]:
        """Search messages by content."""
        repository = get_chat_repository()
        
        if not isinstance(repository, SQLiteChatSessionRepository):
            raise HTTPException(
                status_code=501, 
                detail="Message search only available for SQLite storage"
            )
        
        try:
            results = await repository.search_messages(query, limit)
            return {
                "status": "success",
                "query": query,
                "total_results": len(results),
                "data": results
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching messages: {str(e)}")
    
    async def export_data(
        self,
        chat_id: Optional[str] = Query(None, description="Specific chat ID to export"),
        format: str = Query("json", description="Export format (currently only json)")
    ) -> FileResponse:
        """Export chat data to a file."""
        repository = get_chat_repository()
        
        if not isinstance(repository, SQLiteChatSessionRepository):
            raise HTTPException(
                status_code=501, 
                detail="Data export only available for SQLite storage"
            )
        
        try:
            # Parse chat_id if provided
            chat_uuid = None
            if chat_id:
                try:
                    chat_uuid = UUID(chat_id)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid chat ID format")
            
            # Create temporary file for export
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                export_data = await repository.export_chat_data(chat_uuid)
                json.dump(export_data, tmp_file, indent=2, ensure_ascii=False)
                tmp_file_path = tmp_file.name
            
            # Determine filename
            if chat_uuid:
                filename = f"chat_export_{chat_id}.json"
            else:
                filename = f"full_chat_export_{export_data['export_timestamp'].replace(':', '-')}.json"
            
            return FileResponse(
                path=tmp_file_path,
                filename=filename,
                media_type='application/json'
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")
    
    async def import_data(
        self,
        background_tasks: BackgroundTasks,
        # Note: In a real implementation, you'd handle file upload here
        # For now, this is a placeholder that expects a JSON file path
        file_path: str = Query(..., description="Path to JSON file to import")
    ) -> Dict[str, Any]:
        """Import chat data from a JSON file."""
        repository = get_chat_repository()
        
        if not isinstance(repository, SQLiteChatSessionRepository):
            raise HTTPException(
                status_code=501, 
                detail="Data import only available for SQLite storage"
            )
        
        try:
            # Verify file exists
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Import file not found")
            
            # Create migration instance and import
            migration = ChatStorageMigration(repository)
            result = await migration.import_from_json(file_path)
            
            return {
                "status": "success",
                "data": result
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error importing data: {str(e)}")
    
    async def cleanup_old_chats(
        self,
        days_old: int = Query(30, ge=1, le=365, description="Delete chats older than this many days")
    ) -> Dict[str, Any]:
        """Delete chats older than specified days."""
        repository = get_chat_repository()
        
        if not isinstance(repository, SQLiteChatSessionRepository):
            raise HTTPException(
                status_code=501, 
                detail="Cleanup only available for SQLite storage"
            )
        
        try:
            deleted_count = await repository.cleanup_old_chats(days_old)
            return {
                "status": "success",
                "message": f"Deleted {deleted_count} chats older than {days_old} days",
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")
    
    async def create_backup(self) -> Dict[str, Any]:
        """Create a backup of the database."""
        repository = get_chat_repository()
        
        if not isinstance(repository, SQLiteChatSessionRepository):
            raise HTTPException(
                status_code=501, 
                detail="Backup only available for SQLite storage"
            )
        
        try:
            # Get database path
            db_path = repository.db_path
            
            # Create backup filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{db_path}.backup_{timestamp}"
            
            # Copy database file
            import shutil
            shutil.copy2(db_path, backup_path)
            
            # Get statistics for the backup
            stats = await repository.get_chat_statistics()
            
            return {
                "status": "success",
                "message": "Backup created successfully",
                "backup_path": backup_path,
                "backup_timestamp": timestamp,
                "stats": stats
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating backup: {str(e)}")
