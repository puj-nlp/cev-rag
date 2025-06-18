"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.config import config_service
from .infrastructure.dependencies import get_vector_database, get_chat_use_case, get_question_answering_use_case
from .adapters.controllers.controllers import ChatController, QuestionController, HealthController


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Get configuration
    api_config = config_service.api
    
    # Create FastAPI app
    app = FastAPI(
        title=api_config.title,
        description=api_config.description,
        version=api_config.version
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize controllers
    health_controller = HealthController()
    chat_controller = ChatController(get_chat_use_case())
    question_controller = QuestionController(get_question_answering_use_case())
    
    # Register routes
    app.include_router(health_controller.router)
    app.include_router(chat_controller.router)
    app.include_router(question_controller.router)
    
    # Verify system configuration on startup
    @app.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        print("Starting RAG API with Hexagonal Architecture...")
        
        # Run system validation
        from .infrastructure.startup_validator import StartupValidator
        
        try:
            validation_results = await StartupValidator.validate_system()
            StartupValidator.print_validation_results(validation_results)
            
            if validation_results["status"] == "error":
                print("⚠️  System validation failed! Some features may not work correctly.")
            elif validation_results["status"] == "warning":
                print("⚠️  System validation completed with warnings.")
            else:
                print("✅ System validation successful!")
                
        except Exception as e:
            print(f"❌ System validation error: {e}")
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
