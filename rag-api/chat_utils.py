import json
import uuid
from typing import Dict, List, Any
from models import ChatSession, Message

def load_chats_from_file(file_path: str) -> Dict[str, ChatSession]:
    """
    Loads chats from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict[str, ChatSession]: Dictionary of chats
    """
    try:
        with open(file_path, "r") as f:
            chats_data = json.load(f)
            
        chats = {}
        for chat_id, chat_data in chats_data.items():
            messages = [Message(**msg) for msg in chat_data.get("messages", [])]
            chat_session = ChatSession(
                id=chat_id,
                title=chat_data.get("title", "Untitled Chat"),
                messages=messages,
                created_at=chat_data.get("created_at"),
                updated_at=chat_data.get("updated_at")
            )
            chats[chat_id] = chat_session
            
        return chats
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is malformed, return an empty dictionary
        return {}

def save_chats_to_file(chats: Dict[str, ChatSession], file_path: str) -> None:
    """
    Saves chats to a JSON file.
    
    Args:
        chats: Dictionary of chats
        file_path: Path to the JSON file
    """
    chats_data = {}
    for chat_id, chat_session in chats.items():
        chats_data[chat_id] = chat_session.dict()
    
    with open(file_path, "w") as f:
        json.dump(chats_data, f, indent=2)

def generate_title_for_chat(question: str, answer: str) -> str:
    """
    Generates a title for the chat based on the first question and response.
    
    Args:
        question: User's first question
        answer: System's first response
        
    Returns:
        str: Generated title
    """
    # Limit the length of the question for the title
    max_length = 40
    if len(question) > max_length:
        title = question[:max_length] + "..."
    else:
        title = question
        
    return title
