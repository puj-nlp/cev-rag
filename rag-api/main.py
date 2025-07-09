"""Main entry point for the RAG API application with Hexagonal Architecture."""

from src.main import app

# Export the app for uvicorn
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
