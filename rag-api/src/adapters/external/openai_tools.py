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
            
            print(f"Getting RAG context for question: {question}")
            
            # Generate embedding
            embedding = await embedding_service.generate_embedding(question)
            print(f"Generated embedding with dimension: {len(embedding)}")
            
            # Search documents
            documents = await vector_db.search_similar_documents(embedding, limit=5)
            print(f"Found {len(documents)} documents from vector search")
            
            if not documents:
                print("WARNING: No documents found in vector search")
                return {
                    "context": "No se encontraron documentos relevantes en la base de datos para esta consulta.",
                    "documents": []
                }
            
            # Build context
            rag_context = await context_builder.build_context(documents, question)
            print(f"Built context with {len(rag_context.documents)} documents")
            
            # Build context with proper formatting
            formatted_context_pieces = []
            documents_metadata = []
            
            for doc in rag_context.documents:
                # Extract metadata consistently
                title = doc.metadata.get("title") or doc.original_fields.get("title") or "Untitled document"
                url = doc.metadata.get("link") or doc.metadata.get("url") or ""
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
            
            print(f"Final formatted context length: {len(formatted_context)} characters")
            
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
        "content": """You are 'Window to Truth', an academic researcher specialized in the Colombian conflict and the Truth Commission. Generate responses based EXCLUSIVELY on the provided information following this EXACT format:

RESPONSE FORMAT:
- Write in Spanish (unless specifically asked otherwise)
- Structure responses in 2-3 concise, well-developed paragraphs maximum
- Each paragraph should focus on one main concept or aspect
- Use in-text citations in brackets [1], [2], [3] etc. for all claims
- End with a "Sources" section listing all references
- Keep responses CONCISE but comprehensive (content: 300-500 words, sources section additional)

PARAGRAPH STRUCTURE:
- Start each paragraph with a clear topic sentence defining the concept
- Develop the idea with specific details from the sources
- Include concrete examples, data, or testimonies when available
- Use academic, formal Spanish language
- Connect concepts logically between paragraphs
- Be direct and avoid repetitive information

CITATION REQUIREMENTS:
- Use ONLY numbered citations [1], [2], [3] throughout the text (no "Ver fuente" or other text)
- Each significant claim or concept must be cited
- Multiple citations can be used in the same sentence if needed: [1][2]
- Cite page numbers when specific information is referenced
- Start citations from [1] and continue sequentially
- Do NOT include any links or additional text in citations

SOURCES SECTION FORMAT:
After the main text, include:
"Sources" (exactly as shown)
1. Full document title. (Year). Publisher. ISBN (if available)., Page X. https://full-url-here.com
2. Full document title. (Year). Publisher. ISBN (if available)., Page X. https://full-url-here.com
3. Full document title. (Year). Publisher. ISBN (if available)., Page X. https://full-url-here.com

The Sources section must include ALL documents referenced by the numbered citations [1], [2], [3], etc.

CONTENT GUIDELINES:
- Base responses EXCLUSIVELY on provided information
- DO NOT reveal victim names or specific locations that could endanger individuals
- Use precise, objective language
- Present comprehensive information while maintaining academic rigor
- Focus on concepts, policies, and documented findings from the Truth Commission
- Explain complex concepts clearly for academic audience
- Keep responses focused and avoid unnecessary elaboration

EXAMPLE STRUCTURE:
La "Paz Grande" es un concepto desarrollado por la Comisión de la Verdad de Colombia para describir un futuro en el que se supere el legado del conflicto armado mediante la verdad, el reconocimiento y la reconciliación [1]. La Comisión hace un llamado a la sociedad colombiana a acoger las verdades de la tragedia del conflicto [2].

La "Paz Grande" también se refiere al entendimiento del conflicto armado en Colombia como parte de un complejo entramado de factores políticos, económicos, culturales y de narcotráfico, donde las responsabilidades son compartidas y colectivas [3].

Sources
1. Convocatoria a la paz grande: Declaración de la Comisión para el Esclarecimiento de la Verdad, la Convivencia y la No Repetición. (2022). Colombia. Comisión de la Verdad. ISBN 978-958-53874-3-0., Page 22. https://www.comisiondelaverdad.co/convocatoria-la-paz-grande
2. Convocatoria a la paz grande: Declaración de la Comisión para el Esclarecimiento de la Verdad, la Convivencia y la No Repetición. (2022). Colombia. Comisión de la Verdad. ISBN 978-958-53874-3-0., Page 38. https://www.comisiondelaverdad.co/convocatoria-la-paz-grande
3. Convocatoria a la paz grande: Declaración de la Comisión para el Esclarecimiento de la Verdad, la Convivencia y la No Repetición. (2022). Colombia. Comisión de la Verdad. ISBN 978-958-53874-3-0., Page 46. https://www.comisiondelaverdad.co/convocatoria-la-paz-grande

CRITICAL: Every citation number [1], [2], [3] used in the text MUST have a corresponding entry in the Sources section.

IMPORTANT: Use the get_relevant_information tool to find comprehensive information about the topic before responding."""
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
                # Format the response with sources section
                formatted_response, filtered_references = _format_response_with_sources(
                    response_message.content, 
                    collected_contexts
                )
                return {
                    "content": formatted_response,
                    "is_bot": True,
                    "contexts": collected_contexts,
                    "references": filtered_references
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
        
        # Format the final response with sources section
        formatted_final_response, filtered_references = _format_response_with_sources(
            final_response.choices[0].message.content, 
            collected_contexts
        )
        
        return {
            "content": formatted_final_response,
            "is_bot": True,
            "contexts": collected_contexts,
            "references": filtered_references
        }
    
    except Exception as e:
        print(f"Error in final response: {e}")
        return {
            "content": f"An error occurred while generating the final response: {str(e)}",
            "is_bot": True,
            "error": True,
            "contexts": collected_contexts
        }


def _format_response_with_sources(content: str, collected_contexts: List[Dict]) -> tuple[str, List[Dict]]:
    """Format the response with a proper Sources section in the desired style."""
    if not collected_contexts:
        return content, []
    
    # Extract references
    
    references = _extract_references_from_contexts(collected_contexts)
    if not references:
        return content, []
    
    # If content already has a Sources section, remove it to replace with our enhanced version
    import re
    
    # Check if there's already a Sources section and remove it
    sources_pattern = r'\n\nSources\n.*$'
    if "Sources" in content:
        print("DEBUG: Found existing Sources section, will replace it with URLs")
        content = re.sub(sources_pattern, '', content, flags=re.DOTALL)
    elif "Fuentes" in content:
        print("DEBUG: Found existing Fuentes section, will replace it with URLs")
        fuentes_pattern = r'\n\nFuentes\n.*$'
        content = re.sub(fuentes_pattern, '', content, flags=re.DOTALL)
    
    # Find all citation numbers in the content to ensure we have all referenced sources
    import re
    cited_numbers = set()
    citation_matches = re.findall(r'\[(\d+)\]', content)
    for match in citation_matches:
        cited_numbers.add(int(match))
    
    # Build sources section with all cited references
    sources_section = "\n\nSources"
    
    # If we have cited numbers, use them to determine how many sources to include
    if cited_numbers:
        max_sources = max(cited_numbers)
        # Ensure we don't exceed available references
        max_sources = min(max_sources, len(references))
    else:
        # If no citations found, include first 3 references
        max_sources = min(3, len(references))
    
    # Filter references to only include those that will be shown in Sources section
    filtered_references = references[:max_sources]

    for i in range(max_sources):
        if i < len(references):
            ref = references[i]
            source_line = f"\n{i+1}. {ref['title']}. ({ref['year']}). {ref['publisher']}."
            if ref.get('isbn'):
                source_line += f" ISBN {ref['isbn']}."
            if ref.get('page'):
                source_line += f", Page {ref['page']}."
            # Incluir la URL con texto descriptivo si existe en los datos de Milvus
            if ref.get('url'):
                print(f"DEBUG: Reference {i+1} has URL: {ref['url']}")
                source_line += f" [Ver documento]({ref['url']})"
            else:
                print(f"DEBUG: Reference {i+1} has no URL. Full ref: {ref}")
            sources_section += source_line
    
    return content + sources_section, filtered_references


def _extract_references_from_contexts(collected_contexts: List[Dict]) -> List[Dict]:
    """Extract references from collected contexts for citation purposes."""
    references = []
    ref_number = 1
    seen_references = set()  # To avoid duplicate references
    
    for context_data in collected_contexts:
        documents = context_data.get("documents", [])
        for doc in documents:  # Include ALL documents, not just first 3
            source_id = doc.get("source_id", "")
            page = str(doc.get("page", ""))
            title = doc.get("title", "Untitled document")
            
            # Create a unique identifier to avoid duplicates
            unique_id = f"{title}_{page}"
            if unique_id in seen_references:
                continue
            seen_references.add(unique_id)
            
            # Get URL specifically from the "link" field in Milvus
            url = None
            print(f"DEBUG: Full document structure: {doc}")
            
            # First check if there's a direct link field
            if "link" in doc:
                url = doc["link"]
                print(f"DEBUG: Direct link field found: {url}")
            
            # Check metadata
            if not url and "metadata" in doc:
                metadata = doc["metadata"]
                print(f"DEBUG: Metadata keys: {list(metadata.keys()) if metadata else 'No metadata'}")
                if metadata:
                    url = metadata.get("link") or metadata.get("url")
                    print(f"DEBUG: From metadata - URL: {url}")
            
            # Check original_fields
            if not url and "original_fields" in doc:
                original_fields = doc["original_fields"]
                print(f"DEBUG: Original fields keys: {list(original_fields.keys()) if original_fields else 'No original_fields'}")
                if original_fields:
                    url = original_fields.get("link") or original_fields.get("url")
                    print(f"DEBUG: From original_fields - URL: {url}")
            
            # Si aún no se encuentra URL, comprobar si el campo 'link' existe con otro nombre
            if not url and "metadata" in doc and doc["metadata"]:
                # Verificar todos los campos que puedan contener enlaces
                for key in doc["metadata"]:
                    if key.lower() in ["link", "url", "enlace", "web", "website"]:
                        url = doc["metadata"][key]
                        print(f"DEBUG: Found URL in metadata key '{key}': {url}")
                        break
            
            print(f"DEBUG: Final URL for reference {ref_number}: {url}")
            
            # No agregar URLs predeterminadas - usar solo la URL que viene de Milvus
            
            references.append({
                "number": ref_number,
                "title": title,
                "source_id": source_id,
                "page": page,
                "year": "2022",
                "publisher": "CEV",
                "isbn": "978-958-53874-3-0",
                "url": url  # Usar el valor real de la URL
            })
            ref_number += 1
            
            # Increased limit to ensure enough references for citations but not too many
            if ref_number > 8:
                break
        
        if ref_number > 8:
            break
    
    return references
