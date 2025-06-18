"""OpenAI tools implementation for RAG context retrieval."""

import json
from typing import List, Dict, Any
from openai import OpenAI

# Function definition for tool calling
RAG_FUNCTION = {
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


def get_rag_context_for_tools(question: str) -> dict:
    """
    Gets relevant RAG context for a specific question for use with tools.
    This function interfaces with the existing RAG infrastructure.
    """
    try:
        # Import here to avoid circular dependencies
        from ...infrastructure.dependencies import get_vector_database, get_embedding_service, get_context_builder
        import asyncio
        
        async def _get_context():
            vector_db = get_vector_database()
            embedding_service = get_embedding_service()
            context_builder = get_context_builder()
            
            # Generate embedding
            embedding = await embedding_service.generate_embedding(question)
            
            # Search documents
            documents = await vector_db.search_similar_documents(embedding, limit=5)
            
            # Build context
            rag_context = await context_builder.build_context(documents, question)
            
            # Build context with proper formatting
            formatted_context_pieces = []
            documents_metadata = []
            
            for doc in rag_context.documents:
                # Extract metadata consistently
                title = doc.metadata.get("title") or doc.original_fields.get("title") or "Untitled document"
                url = doc.metadata.get("link", "")
                page = doc.metadata.get("page") or doc.original_fields.get("page") or ""
                source_id = doc.metadata.get("source_id") or doc.original_fields.get("source_id") or ""
                
                # Format each piece consistently
                formatted_piece = f"Source: {title}\n"
                if url:
                    formatted_piece += f"URL: {url}\n"
                if page:
                    formatted_piece += f"Page number: {page}\n"
                formatted_piece += f"Text: {doc.content}"
                
                formatted_context_pieces.append(formatted_piece)
                
                # Store metadata for reference extraction
                documents_metadata.append({
                    "title": title,
                    "page": page,
                    "source_id": source_id,
                    "metadata": doc.metadata,
                    "original_fields": doc.original_fields,
                    "score": doc.score
                })
            
            # Join all context pieces with separators
            formatted_context = "\n\n---\n\n".join(formatted_context_pieces)
            
            return {
                "context": formatted_context,
                "documents": documents_metadata
            }
        
        # Create new event loop for this thread if none exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, use asyncio.create_task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _get_context())
                    return future.result()
            else:
                return loop.run_until_complete(_get_context())
        except RuntimeError:
            # No event loop in current thread, create new one
            return asyncio.run(_get_context())
        
    except Exception as e:
        print(f"Error getting RAG context for tools: {e}")
        return {
            "context": f"Could not retrieve relevant information due to: {str(e)}",
            "documents": []
        }


def generate_answer_with_tools(question: str, chat_history: List[Dict], client: OpenAI) -> Dict[str, Any]:
    """
    Generates a response using OpenAI with the ability to call tools for more context.
    
    Args:
        question: User's question
        chat_history: Conversation history
        client: OpenAI client instance
        
    Returns:
        Dict: Generated response and metadata
    """
    # System message with detailed academic guidelines
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
    
    # Add relevant chat history (last 5 messages)
    relevant_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
    for message in relevant_history:
        role = "assistant" if message["is_bot"] else "user"
        messages.append({"role": role, "content": message["content"]})
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    # List to collect all contextual information obtained
    collected_contexts = []
    
    # Conversation loop with tools (max 3 turns to avoid loops)
    max_turns = 3
    
    for turn in range(max_turns):
        try:
            # Call OpenAI API with tools
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=[{
                    "type": "function",
                    "function": RAG_FUNCTION
                }],
                tool_choice="auto",
                temperature=0.3
            )
            
            # Get the response message
            response_message = response.choices[0].message
            
            # Add the message to history
            messages.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": response_message.tool_calls
            })
            
            # Check if there are tool calls
            tool_calls = response_message.tool_calls
            
            # If there are no tool calls, return the final response
            if not tool_calls:
                return {
                    "content": response_message.content,
                    "is_bot": True,
                    "contexts": collected_contexts,
                    "references": _extract_references_from_contexts(collected_contexts)
                }
            
            # Process each tool call
            for tool_call in tool_calls:
                if tool_call.function.name == "get_relevant_information":
                    # Extract arguments
                    func_args = json.loads(tool_call.function.arguments)
                    subquestion = func_args.get("question")
                    
                    if not subquestion:
                        continue
                    
                    print(f"Tool called for turn {turn + 1} with question: {subquestion}")
                    
                    # Get RAG context for the sub-question
                    rag_result = get_rag_context_for_tools(subquestion)
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
            print(f"Error in OpenAI API call on turn {turn + 1}: {e}")
            return {
                "content": f"An error occurred while processing your question: {str(e)}",
                "is_bot": True,
                "error": True,
                "contexts": collected_contexts
            }
    
    # If we reach the turn limit, generate final response with all collected context
    try:
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        
        return {
            "content": final_response.choices[0].message.content,
            "is_bot": True,
            "contexts": collected_contexts,
            "references": _extract_references_from_contexts(collected_contexts)
        }
    
    except Exception as e:
        print(f"Error in final response: {e}")
        return {
            "content": f"An error occurred while generating the final response: {str(e)}",
            "is_bot": True,
            "error": True,
            "contexts": collected_contexts
        }


def _extract_references_from_contexts(collected_contexts: List[Dict]) -> List[Dict]:
    """Extract references from collected contexts for citation purposes."""
    references = []
    ref_number = 1
    
    for context_data in collected_contexts:
        documents = context_data.get("documents", [])
        for doc in documents[:3]:  # Limit to first 3 documents per context
            references.append({
                "number": ref_number,
                "title": doc.get("title", "Untitled document"),
                "source_id": doc.get("source_id", ""),
                "page": str(doc.get("page", "")),
                "year": "2022",
                "publisher": "Colombia. Comisión de la Verdad",
                "isbn": "978-958-53874-3-0"
            })
            ref_number += 1
            
            # Limit total references to avoid overwhelming response
            if ref_number > 10:
                break
        
        if ref_number > 10:
            break
    
    return references
