"""
Document Storage

Handles document loading, chunking, and storage.
Provides interfaces for working with different document types.
"""

import logging
import os
import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..config import env
from . import vector_store

# Configure logger
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document for processing and storage."""
    
    text: str
    """The text content of the document."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Metadata associated with the document."""
    
    id: Optional[str] = None
    """Unique identifier for the document. Generated if not provided."""
    
    def __post_init__(self):
        """Initialize document with default values if needed."""
        if self.id is None:
            self.id = str(uuid.uuid4())
        
        # Ensure created_at exists in metadata
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.now().isoformat()


class DocumentLoader(ABC):
    """Base class for document loaders."""
    
    @abstractmethod
    def load(self) -> List[Document]:
        """
        Load documents from source.
        
        Returns:
            List of Document objects
        """
        pass


class TextLoader(DocumentLoader):
    """Load document from a text string."""
    
    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize text loader.
        
        Args:
            text: Text content to load
            metadata: Optional metadata for the document
        """
        self.text = text
        self.metadata = metadata or {}
    
    def load(self) -> List[Document]:
        """
        Load document from text.
        
        Returns:
            List containing a single Document
        """
        return [Document(text=self.text, metadata=self.metadata)]


class FileLoader(DocumentLoader):
    """Load document from a file."""
    
    def __init__(
        self,
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize file loader.
        
        Args:
            file_path: Path to the file to load
            encoding: Text encoding of the file
            metadata: Optional metadata for the document
        """
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.metadata = metadata or {}
    
    def load(self) -> List[Document]:
        """
        Load document from file.
        
        Returns:
            List containing a single Document
        
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        # Read the file content
        with open(self.file_path, "r", encoding=self.encoding) as f:
            text = f.read()
        
        # Add file metadata
        metadata = self.metadata.copy()
        metadata.update({
            "source": str(self.file_path),
            "filename": self.file_path.name,
            "filetype": self.file_path.suffix.lstrip(".").lower(),
            "filesize": self.file_path.stat().st_size,
            "modified_at": datetime.fromtimestamp(self.file_path.stat().st_mtime).isoformat()
        })
        
        return [Document(text=text, metadata=metadata)]


class DirectoryLoader(DocumentLoader):
    """Load documents from a directory."""
    
    def __init__(
        self,
        directory_path: Union[str, Path],
        glob_pattern: str = "**/*.*",
        exclude_pattern: Optional[str] = None,
        encoding: str = "utf-8",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize directory loader.
        
        Args:
            directory_path: Path to the directory to load
            glob_pattern: Pattern for matching files
            exclude_pattern: Pattern for excluding files
            encoding: Text encoding of the files
            metadata: Optional metadata for the documents
        """
        self.directory_path = Path(directory_path)
        self.glob_pattern = glob_pattern
        self.exclude_pattern = exclude_pattern
        self.encoding = encoding
        self.metadata = metadata or {}
    
    def load(self) -> List[Document]:
        """
        Load documents from directory.
        
        Returns:
            List of Document objects
        
        Raises:
            FileNotFoundError: If the directory doesn't exist
        """
        if not self.directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {self.directory_path}")
        
        documents = []
        
        # Get all matching files
        files = list(self.directory_path.glob(self.glob_pattern))
        
        # Apply exclude pattern if provided
        if self.exclude_pattern:
            exclude_regex = re.compile(self.exclude_pattern)
            files = [f for f in files if not exclude_regex.search(str(f))]
        
        # Load each file
        for file_path in files:
            if file_path.is_file():
                try:
                    # Use FileLoader to load the document
                    file_loader = FileLoader(
                        file_path=file_path,
                        encoding=self.encoding,
                        metadata=self.metadata.copy()
                    )
                    
                    documents.extend(file_loader.load())
                except Exception as e:
                    logger.warning(f"Error loading file {file_path}: {e}")
        
        return documents


class DocumentChunker:
    """Split documents into smaller chunks for processing."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = ["\n\n", "\n", ". ", " ", ""]
    ):
        """
        Initialize document chunker.
        
        Args:
            chunk_size: Target size of chunks in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting, in priority order
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        # If text is smaller than chunk size, return it as is
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        
        # Try each separator in turn
        for separator in self.separators:
            if separator == "":
                # If no separator works, fall back to character-level splitting
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                    # Get chunk of appropriate size
                    chunk = text[i:i + self.chunk_size]
                    if chunk:
                        chunks.append(chunk)
                break
            
            # Split text by separator
            splits = text.split(separator)
            
            # Skip if separator doesn't actually split the text
            if len(splits) == 1:
                continue
            
            # Build chunks by joining splits
            current_chunk = []
            current_chunk_size = 0
            
            for split in splits:
                # Add separator back to split (except for empty separator)
                if separator:
                    piece = split + separator
                else:
                    piece = split
                
                # If adding this piece would exceed chunk size, store current chunk and start a new one
                if current_chunk and current_chunk_size + len(piece) > self.chunk_size:
                    # Join current chunk parts and add to chunks
                    chunks.append("".join(current_chunk))
                    
                    # Start new chunk with overlap
                    overlap_start = max(0, len("".join(current_chunk)) - self.chunk_overlap)
                    new_current_chunk = ["".join(current_chunk)[overlap_start:]]
                    current_chunk = new_current_chunk
                    current_chunk_size = len(current_chunk[0])
                
                # Add piece to current chunk
                current_chunk.append(piece)
                current_chunk_size += len(piece)
            
            # Add the last chunk if it's not empty
            if current_chunk:
                chunks.append("".join(current_chunk))
            
            # If we successfully split with this separator, stop trying others
            if chunks:
                break
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: Documents to split
            
        Returns:
            List of chunked documents
        """
        chunked_documents = []
        
        for doc in documents:
            # Split text into chunks
            text_chunks = self.split_text(doc.text)
            
            # Create new Document for each chunk
            for i, chunk in enumerate(text_chunks):
                # Copy metadata and add chunk info
                metadata = doc.metadata.copy()
                metadata["chunk"] = i
                metadata["chunk_of"] = doc.id
                metadata["total_chunks"] = len(text_chunks)
                
                # Create new document
                chunked_doc = Document(
                    text=chunk,
                    metadata=metadata
                )
                
                chunked_documents.append(chunked_doc)
        
        return chunked_documents


class DocumentProcessor:
    """Process and store documents."""
    
    def __init__(
        self,
        chunker: Optional[DocumentChunker] = None,
        vector_store_provider: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize document processor.
        
        Args:
            chunker: Document chunker instance
            vector_store_provider: Vector store provider to use
            **kwargs: Additional parameters for vector store
        """
        self.chunker = chunker or DocumentChunker()
        self.vector_store_provider = vector_store_provider
        self.vector_store_kwargs = kwargs
    
    def process(
        self,
        documents: List[Document],
        chunk: bool = True,
        store: bool = True,
    ) -> List[Document]:
        """
        Process documents by chunking and storing them.
        
        Args:
            documents: Documents to process
            chunk: Whether to chunk documents
            store: Whether to store documents in vector store
            
        Returns:
            Processed documents
        """
        # Chunk documents if requested
        processed_docs = self.chunker.split_documents(documents) if chunk else documents
        
        # Store documents if requested
        if store:
            self.store_documents(processed_docs)
        
        return processed_docs
    
    def store_documents(self, documents: List[Document]) -> List[str]:
        """
        Store documents in vector store.
        
        Args:
            documents: Documents to store
            
        Returns:
            List of document IDs
        """
        # Get vector store
        store = vector_store.get_vector_store(
            provider=self.vector_store_provider,
            **self.vector_store_kwargs
        )
        
        # Prepare data for vector store
        texts = [doc.text for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [doc.id for doc in documents]
        
        # Add to vector store
        return store.add_texts(texts, metadatas, ids)
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Tuple[Document, float]]:
        """
        Search for documents similar to query.
        
        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter
            **kwargs: Additional parameters for vector store
            
        Returns:
            List of (document, score) tuples
        """
        # Get vector store
        store = vector_store.get_vector_store(
            provider=self.vector_store_provider,
            **self.vector_store_kwargs
        )
        
        # Search in vector store
        results = store.search(query, k, filter, **kwargs)
        
        # Convert to Documents
        document_results = []
        for text, metadata, score in results:
            doc = Document(text=text, metadata=metadata, id=metadata.get("chunk_of"))
            document_results.append((doc, score))
        
        return document_results
    
    def delete(self, document_ids: List[str]) -> None:
        """
        Delete documents from vector store.
        
        Args:
            document_ids: IDs of documents to delete
        """
        # Get vector store
        store = vector_store.get_vector_store(
            provider=self.vector_store_provider,
            **self.vector_store_kwargs
        )
        
        # Delete from vector store
        store.delete(document_ids)


# Convenience functions

def load_document(text: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
    """
    Load a document from text.
    
    Args:
        text: Text content
        metadata: Optional metadata
        
    Returns:
        Document instance
    """
    loader = TextLoader(text, metadata)
    return loader.load()[0]


def load_file(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    metadata: Optional[Dict[str, Any]] = None
) -> Document:
    """
    Load a document from a file.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        metadata: Optional metadata
        
    Returns:
        Document instance
    """
    loader = FileLoader(file_path, encoding, metadata)
    return loader.load()[0]


def load_directory(
    directory_path: Union[str, Path],
    glob_pattern: str = "**/*.*",
    exclude_pattern: Optional[str] = None,
    encoding: str = "utf-8",
    metadata: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """
    Load documents from a directory.
    
    Args:
        directory_path: Path to directory
        glob_pattern: Pattern for matching files
        exclude_pattern: Pattern for excluding files
        encoding: File encoding
        metadata: Optional metadata
        
    Returns:
        List of Document instances
    """
    loader = DirectoryLoader(directory_path, glob_pattern, exclude_pattern, encoding, metadata)
    return loader.load()


def process_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    chunk: bool = True,
    store: bool = True,
    vector_store_provider: Optional[str] = None,
    **kwargs
) -> List[Document]:
    """
    Process and store documents.
    
    Args:
        documents: Documents to process
        chunk_size: Size of chunks in characters
        chunk_overlap: Overlap between chunks
        chunk: Whether to chunk documents
        store: Whether to store in vector store
        vector_store_provider: Vector store provider
        **kwargs: Additional vector store parameters
        
    Returns:
        Processed documents
    """
    chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    processor = DocumentProcessor(
        chunker=chunker,
        vector_store_provider=vector_store_provider,
        **kwargs
    )
    
    return processor.process(documents, chunk=chunk, store=store)


def search_documents(
    query: str,
    k: int = 4,
    filter: Optional[Dict[str, Any]] = None,
    vector_store_provider: Optional[str] = None,
    **kwargs
) -> List[Tuple[Document, float]]:
    """
    Search for documents similar to query.
    
    Args:
        query: Query text
        k: Number of results to return
        filter: Optional metadata filter
        vector_store_provider: Vector store provider
        **kwargs: Additional vector store parameters
        
    Returns:
        List of (document, score) tuples
    """
    processor = DocumentProcessor(
        vector_store_provider=vector_store_provider,
        **kwargs
    )
    
    return processor.search(query, k, filter, **kwargs) 