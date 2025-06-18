import json
from typing import List, Dict, Any
from openai import OpenAI
import config
from rag_service import get_embedding, get_abstract_collection, get_documents_from_query

# Definition of the function to be used as a tool
PAGES_GET_FUNCTION = {
    "name": "get_relevant_information",
    "description": "Get document fragments and source material relevant to a question related to the Colombian conflict.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question for which to search relevant information, formulated as a question. For example: What implications does the report have on the relationship between truth and the future? or What role does the Commission see for truth-telling in Colombian society?"
            }
        },
        "required": ["question"]
    }
}

def get_rag_context(question: str) -> dict:
    """
    Gets relevant RAG context for a specific question.
    
    Args:
        question: The question for which to search information
        
    Returns:
        dict: Contains formatted RAG context and document metadata
    """
    try:
        # Get the embedding for the question
        query_vec = get_embedding(question)
        
        # Search in the collection
        abstract_collection = get_abstract_collection()
        search_results = get_documents_from_query(query_vec, abstract_collection)
        
        # Format results for context
        context_pieces = []
        documents_metadata = []
        
        for i, doc in enumerate(search_results):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            original = doc.get("original_fields", {})
            
            # Create a consistent format for each fragment
            source_title = metadata.get("title") or original.get("title") or "Untitled document"
            source_url = metadata.get("link", "")
            page_number = metadata.get("page") or original.get("page") or ""
            source_id = metadata.get("source_id") or original.get("source_id") or ""
            
            formatted_piece = f"Source: {source_title}\n"
            if source_url:
                formatted_piece += f"URL: {source_url}\n"
            if page_number:
                formatted_piece += f"Page number: {page_number}\n"
            formatted_piece += f"Text: {content}"
            
            context_pieces.append(formatted_piece)
            
            # Store document metadata for reference extraction
            documents_metadata.append({
                "title": source_title,
                "page": page_number,
                "source_id": source_id,
                "metadata": metadata,
                "original_fields": original,
                "score": doc.get("score", 0)
            })
        
        # Join all context pieces
        context = "\n\n---\n\n".join(context_pieces)
        
        return {
            "context": context,
            "documents": documents_metadata
        }
    
    except Exception as e:
        print(f"Error getting RAG context: {e}")
        return {
            "context": f"Could not retrieve relevant information due to: {str(e)}",
            "documents": []
        }

def generate_answer_with_tools(question: str, chat_history: List[Dict]) -> Dict[str, Any]:
    """
    Generates a response using OpenAI with the ability to call tools for more context.
    
    Args:
        question: User's question
        chat_history: Conversation history
        
    Returns:
        Dict: Generated response and metadata
    """
    # OpenAI client
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    # System message
    system_message = {
        "role": "system", 
        "content": """You are 'Window to Truth', an academic researcher specialized in the Colombian conflict and the Truth Commission. Generate detailed and rigorous responses based EXCLUSIVELY on the provided information. Follow these specific guidelines:

1. STRICT ACADEMIC FORMAT:
   - Begin with a clear "Introduction" that presents the general topic.
   - Use bold subtitles to organize information by regions, themes, or concepts.
   - When mentioning specific data, ALWAYS include the citation in IEEE format [number] at the end of the sentence.
   - End with a "Conclusion" that synthesizes the main points.

2. CITATIONS AND REFERENCES:
   - SPECIFICALLY cite pages and exact sources from the documents.
   - Use the format [number] for in-text citations.
   - At the end, include a "References" section with the complete format: [number] Document title, page X.

3. CONTENT, ETHICS, AND TONE:
   - Treat topics with academic rigor and ethical sensitivity due to the nature of the conflict.
   - DO NOT reveal names of victims, specific locations of sensitive events, or details that could endanger individuals or communities.
   - Use precise, objective, and formal language; avoid emotionally charged terms.
   - Base your responses EXCLUSIVELY on the provided information; do not make assumptions.
   - Maintain neutrality and avoid bias towards any actor in the conflict.

4. RESPONSIBILITY AND ATTRIBUTION:
   - Focus on systemic factors, institutional roles, and collective responsibility rather than blaming specific individuals.
   - Analyze the broader context and the interaction of various actors in the conflict.

5. INFORMATION MANAGEMENT:
   - If you need specific information, use the get_relevant_information function to search for it.
   - If sources present conflicts or ambiguities, acknowledge it and present the different perspectives.

IMPORTANT: USE the get_relevant_information tool to search for specific information about aspects of the Colombian conflict. You can use this tool multiple times to refine your search."""
    }
    
    # Initialize messages
    messages = [system_message]
    
    # Add relevant chat history
    relevant_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
    for message in relevant_history:
        role = "assistant" if message["is_bot"] else "user"
        messages.append({"role": role, "content": message["content"]})
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    # List to collect all contextual information obtained
    collected_contexts = []
    
    # Conversation loop with tools
    max_turns = 3  # Limit the maximum number of turns to avoid loops
    
    for _ in range(max_turns):
        # Llamar a la API de OpenAI
        try:
            response = client.chat.completions.create(
                model=config.COMPLETION_MODEL,
                messages=messages,
                tools=[{
                    "type": "function",
                    "function": PAGES_GET_FUNCTION
                }],
                tool_choice="auto",
                temperature=0.3
            )
            
            # Get the response message
            response_message = response.choices[0].message
            
            # Add the message to history
            messages.append(response_message.model_dump())
            
            # Check if there are tool calls
            tool_calls = response_message.tool_calls
            
            # If there are no tool calls, return the final response
            if not tool_calls:
                return {
                    "content": response_message.content,
                    "is_bot": True,
                    "contexts": collected_contexts
                }
            
            # Process each tool call
            for tool_call in tool_calls:
                if tool_call.function.name == "get_relevant_information":
                    # Extraer argumentos
                    func_args = json.loads(tool_call.function.arguments)
                    subquestion = func_args.get("question")
                    
                    if not subquestion:
                        continue
                    
                    # Get RAG context for the sub-question
                    rag_result = get_rag_context(subquestion)
                    context = rag_result["context"]
                    documents = rag_result["documents"]
                    
                    # Store collected context with documents for reference extraction
                    collected_contexts.append({
                        "question": subquestion,
                        "context": context,
                        "documents": documents
                    })
                    
                    # Add the tool response
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "get_relevant_information",
                        "content": context
                    })
        
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")
            return {
                "content": f"An error occurred while processing your question: {str(e)}",
                "is_bot": True,
                "error": True
            }
    
    # If we reach the turn limit, generate final response with all collected context
    try:
        final_response = client.chat.completions.create(
            model=config.COMPLETION_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        
        return {
            "content": final_response.choices[0].message.content,
            "is_bot": True,
            "contexts": collected_contexts
        }
    
    except Exception as e:
        print(f"Error in final response: {e}")
        return {
            "content": f"An error occurred while generating the final response: {str(e)}",
            "is_bot": True,
            "error": True
        }
