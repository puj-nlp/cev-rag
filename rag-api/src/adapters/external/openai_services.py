"""OpenAI service implementations."""

from typing import List, Dict, Any
from openai import OpenAI

from ...domain.ports import EmbeddingService, LLMService


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI implementation of embedding service."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-large", expected_dimension: int = 3072):
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._expected_dimension = expected_dimension
        print(f"Initialized embedding service with model: {model}, expected dimension: {expected_dimension}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text."""
        if not text:
            text = "Empty query"
        
        # Clean the text
        text = text.replace("\n", " ").strip()
        
        try:
            print(f"Generating embedding with model: {self._model}")
            
            # For text-embedding-3-* models, we can specify dimensions
            if "text-embedding-3" in self._model:
                response = self._client.embeddings.create(
                    input=text,
                    model=self._model,
                    dimensions=self._expected_dimension  # Specify the dimension
                )
            else:
                response = self._client.embeddings.create(
                    input=text,
                    model=self._model
                )
            
            embedding = response.data[0].embedding
            print(f"Embedding generated with dimension: {len(embedding)}")
            
            # Verify dimension matches expectation
            if len(embedding) != self._expected_dimension:
                print(f"WARNING: Generated embedding has {len(embedding)} dimensions, expected {self._expected_dimension}")
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise


class OpenAILLMService(LLMService):
    """OpenAI implementation of LLM service."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self._client = OpenAI(api_key=api_key)
        self._model = model
    
    async def generate_answer(
        self, 
        question: str, 
        context: str, 
        chat_history: List[Dict[str, Any]]
    ) -> str:
        """Generate an answer using the LLM."""
        # Build the prompt
        prompt = self._build_prompt(question, context, chat_history)
        
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are 'Window to Truth', an academic researcher specialized in the Colombian conflict and the Truth Commission. Generate CONCRETE, SPECIFIC, and CONCISE responses based EXCLUSIVELY on the provided information. Follow these guidelines:

1. DIRECT AND CONCRETE FORMAT:
   - Start with a clear, direct answer to the question
   - Present SPECIFIC data, numbers, and facts from the documents
   - Use concrete examples and cases mentioned in the sources
   - Include exact references to source documents with page numbers when available
   - Keep responses BRIEF and focused while being informative

2. EVIDENCE-BASED CONTENT:
   - Prioritize specific statistics, figures, and documented facts
   - Quote or paraphrase specific testimonies and findings (without victim names)
   - Mention concrete policies, programs, or institutional actions documented
   - Reference specific time periods, regions, or events when relevant
   - Avoid generalizations - use the specific information from the documents

3. ETHICAL STANDARDS:
   - DO NOT reveal names of victims or specific locations that could endanger individuals
   - Use precise, objective language with concrete details
   - Base responses EXCLUSIVELY on provided information - no assumptions
   - Maintain neutrality while presenting specific documented facts

4. CONCISE STRUCTURE:
   - Lead with the most important concrete information
   - Support with 2-3 key specific data points or examples
   - Include most relevant statistics when available
   - End with a brief synthesis if necessary
   - ALWAYS preserve complete reference citations

Focus on delivering the most essential, actionable information in a concise format while maintaining all references."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise
    
    async def generate_answer_with_tools(
        self, 
        question: str, 
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate an answer using LLM with tool calling capabilities."""
        # Import here to avoid circular imports
        from .openai_tools import generate_answer_with_tools
        result = generate_answer_with_tools(question, chat_history, self._client)
        
        # Ensure all required fields are present for compatibility
        if "is_bot" not in result:
            result["is_bot"] = True
        if "references" not in result:
            result["references"] = []
        if "contexts" not in result:
            result["contexts"] = []
        

            
        return result
    
    def _build_prompt(self, question: str, context: str, chat_history: List[Dict[str, Any]]) -> str:
        """Build the prompt for the LLM."""
        # Build conversation context
        conversation_context = ""
        if chat_history:
            conversation_context = "\n\nConversation history:\n"
            for msg in chat_history[-5:]:  # Last 5 messages
                role = "Assistant" if msg["is_bot"] else "User"
                conversation_context += f"{role}: {msg['content']}\n"

        prompt = f"""Based on the following information from Colombian Truth Commission documents, provide a CONCRETE and SPECIFIC answer.

Context from Truth Commission Documents:
{context}
{conversation_context}

Question: {question}

Instructions:
- Start with a direct answer using SPECIFIC data, numbers, and documented facts from the context
- Include concrete examples, statistics, and measurable outcomes mentioned in the sources
- Quote specific policies, programs, or institutional actions with their documented effects
- Reference exact page numbers and sources when citing specific information
- Use precise figures, percentages, dates, and quantitative data when available
- Focus on actionable, specific information rather than broad generalizations
- If the context contains limited information, clearly state what specific data is available and what is missing
- DO NOT reveal victim names or sensitive locations that could endanger individuals
- Maintain objectivity while presenting concrete documented facts

Provide a focused, data-driven response based exclusively on the given context."""
        
        return prompt
