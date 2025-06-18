"""Service implementations for infrastructure concerns."""

from typing import List
import datetime

from ..domain.entities import Document, Reference, RAGContext
from ..domain.ports import RAGContextBuilder, TimestampService


class DefaultRAGContextBuilder(RAGContextBuilder):
    """Default implementation of RAG context builder."""
    
    async def build_context(self, documents: List[Document], question: str) -> RAGContext:
        """Build RAG context from retrieved documents."""
        context_pieces = []
        references = []
        
        print(f"Building context from {len(documents)} documents")
        
        for i, doc in enumerate(documents):
            # Build context text
            meta_string = ""
            if doc.metadata.get("title"):
                meta_string += f"Title: {doc.metadata['title']}\\n"
            if doc.metadata.get("source_id"):
                meta_string += f"Source: {doc.metadata['source_id']}\\n"
            if doc.metadata.get("page"):
                meta_string += f"Page: {doc.metadata['page']}\\n"
            
            full_content = ""
            if meta_string:
                full_content = f"{meta_string}\\n{doc.content}"
            else:
                full_content = doc.content
            
            if full_content.strip():
                context_pieces.append(full_content)
                print(f"Document {i+1}: Added {len(full_content)} characters to context")
            
            # Build references (only for top 3 documents)
            if i < 3:
                reference = self._build_reference(doc, i + 1)
                references.append(reference)
        
        context_text = "\\n\\n---\\n\\n".join(context_pieces)
        
        if not context_text.strip():
            print("WARNING: No useful context found in documents")
            context_text = "No relevant information was found for this question in the database."
        
        print(f"Total context: {len(context_text)} characters, {len(references)} references")
        
        return RAGContext(
            documents=documents,
            context_text=context_text,
            references=references
        )
    
    def _build_reference(self, document: Document, number: int) -> Reference:
        """Build a bibliographic reference from a document."""
        title = document.metadata.get("title", "Untitled document")
        source_id = document.metadata.get("source_id", "")
        page = document.metadata.get("page", "")
        
        # Normalize source_id
        if not source_id.startswith("Tomo") and "vol" not in source_id.lower():
            if "tomo" in title.lower() or "vol" in title.lower():
                source_id = title
        
        # Convert page to string if it's a number
        if isinstance(page, (int, float)):
            page = str(int(page))
        
        return Reference(
            number=number,
            title=title,
            source_id=source_id,
            page=page,
            year="2022",
            publisher="Colombia. Comisión de la Verdad",
            isbn="978-958-53874-3-0"
        )


class DefaultTimestampService(TimestampService):
    """Default implementation of timestamp service."""
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.datetime.now().isoformat()
