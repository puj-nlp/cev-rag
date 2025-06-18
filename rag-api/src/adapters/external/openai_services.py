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
                        "content": """You are 'Window to Truth', an academic researcher specialized in the Colombian conflict and the Truth Commission. Generate detailed and rigorous responses based EXCLUSIVELY on the provided information. Follow these specific guidelines:

1. STRICT ACADEMIC FORMAT:
   - Begin with a clear "Introduction" that presents the general topic.
   - Use bold subtitles to organize information by regions, themes, or concepts.
   - When mentioning specific data, include references to the source documents.
   - End with a "Conclusion" that synthesizes the main points.

2. CONTENT, ETHICS, AND TONE:
   - Treat topics with academic rigor and ethical sensitivity due to the nature of the conflict.
   - DO NOT reveal names of victims, specific locations of sensitive events, or details that could endanger individuals or communities.
   - Use precise, objective, and formal language; avoid emotionally charged terms.
   - Base your responses EXCLUSIVELY on the provided information; do not make assumptions.
   - Maintain neutrality and avoid bias towards any actor in the conflict.

3. RESPONSIBILITY AND ATTRIBUTION:
   - Focus on systemic factors, institutional roles, and collective responsibility rather than blaming specific individuals.
   - Analyze the broader context and the interaction of various actors in the conflict.

Always provide comprehensive answers based on the given context while maintaining academic standards and ethical sensitivity."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
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

        prompt = f"""Based on the following information from Colombian Truth Commission documents, please answer the question with academic rigor and ethical sensitivity.

Context from Truth Commission Documents:
{context}
{conversation_context}

Question: {question}

Instructions:
- Provide a comprehensive and detailed answer based EXCLUSIVELY on the given context
- Structure your response with clear introduction, organized body with subtitles, and conclusion
- Use precise, objective, and formal academic language
- Focus on systemic factors and institutional analysis rather than individual blame
- DO NOT reveal names of victims or specific sensitive locations
- If the context doesn't contain sufficient information, clearly mention this limitation
- Maintain neutrality and avoid bias towards any actor in the conflict

Answer:"""
        
        return prompt
