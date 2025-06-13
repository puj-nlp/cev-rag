import json
import uuid
from typing import Dict, List, Any
from models import ChatSession, Message

def load_chats_from_file(file_path: str) -> Dict[str, ChatSession]:
    """
    Carga los chats desde un archivo JSON.
    
    Args:
        file_path: Ruta al archivo JSON
        
    Returns:
        Dict[str, ChatSession]: Diccionario de chats
    """
    try:
        with open(file_path, "r") as f:
            chats_data = json.load(f)
            
        chats = {}
        for chat_id, chat_data in chats_data.items():
            messages = [Message(**msg) for msg in chat_data.get("messages", [])]
            chat_session = ChatSession(
                id=chat_id,
                title=chat_data.get("title", "Chat sin título"),
                messages=messages,
                created_at=chat_data.get("created_at"),
                updated_at=chat_data.get("updated_at")
            )
            chats[chat_id] = chat_session
            
        return chats
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está mal formateado, devolver un diccionario vacío
        return {}

def save_chats_to_file(chats: Dict[str, ChatSession], file_path: str) -> None:
    """
    Guarda los chats en un archivo JSON.
    
    Args:
        chats: Diccionario de chats
        file_path: Ruta al archivo JSON
    """
    chats_data = {}
    for chat_id, chat_session in chats.items():
        chats_data[chat_id] = chat_session.dict()
    
    with open(file_path, "w") as f:
        json.dump(chats_data, f, indent=2)

def generate_title_for_chat(question: str, answer: str) -> str:
    """
    Genera un título para el chat basado en la primera pregunta y respuesta.
    
    Args:
        question: Primera pregunta del usuario
        answer: Primera respuesta del sistema
        
    Returns:
        str: Título generado
    """
    # Limitar la longitud de la pregunta para el título
    max_length = 40
    if len(question) > max_length:
        title = question[:max_length] + "..."
    else:
        title = question
        
    return title
