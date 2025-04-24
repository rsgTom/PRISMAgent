"""
Document Store

High-level API for storing and retrieving documents with vector embeddings.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..config import env
from .vector_store import get_vector_store

# Configure logger
logger = logging.getLogger(__name__)


class Document:
    """Document class for storing text and metadata."""
    
    def __init__(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None
    ):
        """
        Initialize a document.
        
        Args:
            text: Document text content
            metadata: Document metadata
            id: Document ID (generated if not provided)
        """
        self.text = text
        self.metadata = metadata or {}
        self.id = id or str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary."""
        return cls(
            text=data.get("text", ""),
            metadata=data.get("metadata", {}),
            id=data.get("id")
        )


class DocumentStore:
    """
    Document store for storing and retrieving documents using vector embeddings.
    
    This provides a high-level API for working with documents.
    """
    
    def __init__(
        self,
        collection_name: str = "default",
        vector_store_provider: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the document store.
        
        Args:
            collection_name: Collection/namespace name
            vector_store_provider: Vector store provider (defaults to env)
            **kwargs: Additional vector store configuration
        """
        self.collection_name = collection_name
        self.vector_store = get_vector_store(
            provider=vector_store_provider,
            namespace=collection_name,
            **kwargs
        )
    
    def add_documents(
        self,
        documents: List[Document],
        add_created_at: bool = True
    ) -> List[str]:
        """
        Add documents to the store.
        
        Args:
            documents: List of documents to add
            add_created_at: Whether to add created_at timestamp to metadata
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        # Prepare data for vector store
        texts = []
        metadatas = []
        ids = []
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        for doc in documents:
            texts.append(doc.text)
            
            # Add created_at timestamp if requested
            metadata = doc.metadata.copy()
            if add_created_at and "created_at" not in metadata:
                metadata["created_at"] = timestamp
            
            metadatas.append(metadata)
            ids.append(doc.id)
        
        # Add to vector store
        return self.vector_store.add(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        add_created_at: bool = True
    ) -> List[str]:
        """
        Add texts to the store.
        
        Args:
            texts: List of text content
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            add_created_at: Whether to add created_at timestamp to metadata
            
        Returns:
            List of document IDs
        """
        if not texts:
            return []
        
        # Create Document objects
        documents = []
        
        # Ensure we have metadata for each text
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        for text, metadata, id in zip(texts, metadatas, ids):
            doc = Document(
                text=text,
                metadata=metadata,
                id=id
            )
            documents.append(doc)
        
        # Add documents
        return self.add_documents(documents, add_created_at=add_created_at)
    
    def get_documents(self, ids: List[str]) -> List[Document]:
        """
        Get documents by their IDs.
        
        Args:
            ids: List of document IDs
            
        Returns:
            List of documents
        """
        results = self.vector_store.get(ids)
        
        documents = []
        for result in results:
            doc = Document(
                text=result["text"],
                metadata=result["metadata"],
                id=result["id"]
            )
            documents.append(doc)
        
        return documents
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional filter criteria
            
        Returns:
            List of search results with document, score
        """
        # Search in vector store
        results = self.vector_store.search(
            query=query,
            k=k,
            filter=filter
        )
        
        # Convert to Document objects
        document_results = []
        for result in results:
            doc = Document(
                text=result["text"],
                metadata=result["metadata"],
                id=result["id"]
            )
            
            document_results.append({
                "document": doc,
                "score": result["score"]
            })
        
        return document_results
    
    def delete(self, ids: List[str]) -> None:
        """
        Delete documents by ID.
        
        Args:
            ids: List of document IDs to delete
        """
        self.vector_store.delete(ids)
    
    def clear(self) -> None:
        """Clear all documents in the collection."""
        self.vector_store.clear()


# Document chunking utilities

def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separator: str = "\n"
) -> List[str]:
    """
    Split text into chunks.
    
    Args:
        text: Text to split
        chunk_size: Maximum chunk size (characters)
        chunk_overlap: Overlap between chunks (characters)
        separator: Preferred separator for chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Handle case where text is smaller than chunk size
    if len(text) <= chunk_size:
        return [text]
    
    # Split text by separator
    splits = text.split(separator)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for split in splits:
        # Skip empty splits
        if not split:
            continue
        
        # Add separator back if not the first piece
        if current_chunk:
            split = separator + split
        
        # If adding this split would exceed chunk size, complete the chunk
        if current_length + len(split) > chunk_size and current_chunk:
            # Join the current chunk and add to chunks
            chunks.append("".join(current_chunk))
            
            # Start a new chunk with overlap
            if chunk_overlap > 0:
                # Calculate how much text to keep for overlap
                overlap_start = max(0, len("".join(current_chunk)) - chunk_overlap)
                overlap_text = "".join(current_chunk)[overlap_start:]
                
                # Start new chunk with overlap text
                current_chunk = [overlap_text]
                current_length = len(overlap_text)
            else:
                # No overlap, start empty
                current_chunk = []
                current_length = 0
        
        # Add the current split to the chunk
        current_chunk.append(split)
        current_length += len(split)
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append("".join(current_chunk))
    
    return chunks


def chunk_document(
    document: Document,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separator: str = "\n"
) -> List[Document]:
    """
    Split a document into chunks.
    
    Args:
        document: Document to split
        chunk_size: Maximum chunk size (characters)
        chunk_overlap: Overlap between chunks (characters)
        separator: Preferred separator for chunks
        
    Returns:
        List of document chunks
    """
    # Split the text
    text_chunks = split_text(
        document.text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separator=separator
    )
    
    # If only one chunk, return the original document
    if len(text_chunks) == 1:
        return [document]
    
    # Create a document for each chunk
    chunked_docs = []
    for i, chunk in enumerate(text_chunks):
        # Create metadata for chunk
        chunk_metadata = document.metadata.copy()
        chunk_metadata["chunk"] = i
        chunk_metadata["chunk_count"] = len(text_chunks)
        
        # Keep reference to original document ID
        if "parent_id" not in chunk_metadata:
            chunk_metadata["parent_id"] = document.id
        
        # Create document for chunk
        chunk_doc = Document(
            text=chunk,
            metadata=chunk_metadata,
            id=f"{document.id}_chunk_{i}"
        )
        chunked_docs.append(chunk_doc)
    
    return chunked_docs


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separator: str = "\n"
) -> List[Document]:
    """
    Split multiple documents into chunks.
    
    Args:
        documents: Documents to split
        chunk_size: Maximum chunk size (characters)
        chunk_overlap: Overlap between chunks (characters)
        separator: Preferred separator for chunks
        
    Returns:
        List of document chunks
    """
    all_chunks = []
    
    for doc in documents:
        chunks = chunk_document(
            doc,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator
        )
        all_chunks.extend(chunks)
    
    return all_chunks


# Create a global document store instance
_document_store: Optional[DocumentStore] = None


def get_document_store(
    collection_name: str = "default",
    vector_store_provider: Optional[str] = None,
    **kwargs
) -> DocumentStore:
    """
    Get a document store instance.
    
    If a global instance exists for the collection, returns that.
    Otherwise, creates a new instance.
    
    Args:
        collection_name: Collection/namespace name
        vector_store_provider: Vector store provider (defaults to env)
        **kwargs: Additional vector store configuration
        
    Returns:
        Document store instance
    """
    global _document_store
    
    # Create a new instance if none exists or collection is different
    if _document_store is None or _document_store.collection_name != collection_name:
        _document_store = DocumentStore(
            collection_name=collection_name,
            vector_store_provider=vector_store_provider,
            **kwargs
        )
    
    return _document_store 