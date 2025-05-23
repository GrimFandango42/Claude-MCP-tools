"""Vector storage and similarity search for knowledge notes.

Provides embedding-based similarity search capabilities for knowledge notes.
Uses a simple vector store implementation with SQLite for storage.
"""

import logging
import numpy as np
import pickle
from typing import List, Dict, Any

logger = logging.getLogger('knowledge-memory-mcp.vector_store')

class DummyEmbeddingModel:
    """Simple embedding model that creates random vectors for testing."""
    
    def __init__(self, dimension=384):
        """Initialize with specified embedding dimension.
        
        Args:
            dimension: Size of embedding vectors
        """
        self.dimension = dimension
        logger.info(f"Initialized dummy embedding model")
    
    def embed(self, text: str) -> np.ndarray:
        """Generate a random embedding vector for the given text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            np.ndarray: Embedding vector
        """
        # Create a deterministic but simple embedding based on text
        # This is only for testing - not a real embedding model
        seed = sum(ord(c) for c in text[:100])  # Simple hash of text
        np.random.seed(seed)
        return np.random.rand(self.dimension).astype(np.float32)


class VectorStore:
    """Vector storage and similarity search for knowledge notes."""
    
    def __init__(self, db, embedding_dimension=384):
        """Initialize the vector store.
        
        Args:
            db: Database instance for storage
            embedding_dimension: Size of embedding vectors
        """
        self.db = db
        self.embedding_dimension = embedding_dimension
        
        # Use a simple dummy embedding model 
        # In a real implementation, this would use a proper embedding model
        self.embedding_model = DummyEmbeddingModel(dimension=embedding_dimension)
        logger.info(f"Initialized embedding model with dimension {embedding_dimension}")
        logger.info("Vector store initialized")
    
    def update_embedding(self, note_id: str) -> bool:
        """Update the embedding for a note.
        
        Args:
            note_id: The note's unique ID
            
        Returns:
            bool: True if update was successful
        """
        # Get note content
        cursor = self.db.execute(
            "SELECT title, content FROM notes WHERE id = ?", 
            (note_id,)
        )
        note = cursor.fetchone()
        
        if not note:
            return False
        
        # Generate embedding from title and content
        text = f"{note['title']}\n{note['content']}"
        embedding = self.embedding_model.embed(text)
        
        # Serialize embedding
        embedding_bytes = pickle.dumps(embedding)
        
        # Insert or replace embedding
        self.db.execute(
            """INSERT OR REPLACE INTO note_embeddings 
               (note_id, embedding, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)""",
            (note_id, embedding_bytes)
        )
        
        self.db.commit()
        return True
    
    def get_embedding(self, note_id: str) -> np.ndarray:
        """Get the embedding for a note.
        
        Args:
            note_id: The note's unique ID
            
        Returns:
            np.ndarray: The note's embedding vector
        """
        cursor = self.db.execute(
            "SELECT embedding FROM note_embeddings WHERE note_id = ?",
            (note_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            # No embedding exists, create it
            self.update_embedding(note_id)
            
            # Try again
            cursor = self.db.execute(
                "SELECT embedding FROM note_embeddings WHERE note_id = ?",
                (note_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
        
        # Deserialize embedding
        return pickle.loads(result['embedding'])
    
    def get_similar_notes(self, note_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find notes similar to the specified note using vector similarity.
        
        Args:
            note_id: The note's unique ID
            limit: Maximum number of results
            
        Returns:
            list: Similar notes with similarity scores
        """
        # Get query embedding
        query_embedding = self.get_embedding(note_id)
        if query_embedding is None:
            return []
        
        # Get all embeddings
        cursor = self.db.execute(
            """SELECT note_id, embedding FROM note_embeddings 
               WHERE note_id != ?""",
            (note_id,)
        )
        
        results = []
        for row in cursor.fetchall():
            embedding = pickle.loads(row['embedding'])
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)
            
            results.append({
                'note_id': row['note_id'],
                'similarity': similarity
            })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Get note details for top results
        top_results = []
        for item in results[:limit]:
            cursor = self.db.execute(
                "SELECT id, title FROM notes WHERE id = ?",
                (item['note_id'],)
            )
            note = cursor.fetchone()
            if note:
                top_results.append({
                    'id': note['id'],
                    'title': note['title'],
                    'similarity': round(float(item['similarity']), 4)
                })
        
        return top_results
    
    def get_embedding_count(self) -> int:
        """Get the total number of embeddings.
        
        Returns:
            int: Total embedding count
        """
        cursor = self.db.execute("SELECT COUNT(*) as count FROM note_embeddings")
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            float: Cosine similarity (-1 to 1)
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))