import os
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class RagDict(dict):
    """
    A dictionary-like class that supports fuzzy key matching using embeddings and LLM.
    
    When a key is not found in the dictionary, RagDict will:
    1. Find similar keys using embedding-based similarity search
    2. Use an LLM to select the best matching key
    3. Return the value associated with the selected key
    
    Example:
        car_prices = RagDict({
            "Toyota Camry": 25000,
            "Honda Accord": 27000,
            "Tesla Model 3": 40000
        })
        
        # Direct access works like a normal dict
        price = car_prices["Toyota Camry"]  # Returns 25000
        
        # Fuzzy matching when key is not exact
        price = car_prices["Toyot Camri"]  # Will find "Toyota Camry" and return 25000
    """
    
    def __init__(
        self, 
        *args, 
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-4o-mini",
        similarity_threshold: float = 0.7,
        top_k: int = 3,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a RagDict instance.
        
        Args:
            *args: Arguments to pass to the dict constructor
            embedding_model: OpenAI embedding model to use
            llm_model: OpenAI LLM model to use
            similarity_threshold: Threshold for similarity matching (0-1)
            top_k: Number of top similar keys to consider
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            **kwargs: Keyword arguments to pass to the dict constructor
        """
        super().__init__(*args, **kwargs)
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        
        # Initialize OpenAI client
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Cache for key embeddings
        self._key_embeddings = {}
        self._update_embeddings()
    
    def _update_embeddings(self) -> None:
        """Update embeddings for all keys in the dictionary."""
        keys_to_embed = [k for k in self.keys() if k not in self._key_embeddings]
        
        if not keys_to_embed:
            return
            
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=keys_to_embed
            )
            
            for i, key in enumerate(keys_to_embed):
                self._key_embeddings[key] = response.data[i].embedding
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text string."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding for '{text}': {e}")
            raise
    
    def _find_similar_keys(self, query: str) -> List[Tuple[str, float]]:
        """
        Find keys similar to the query using embedding similarity.
        
        Returns:
            List of (key, similarity_score) tuples sorted by similarity (highest first)
        """
        if not self:
            return []
            
        # Get embedding for query
        query_embedding = self._get_embedding(query)
        
        # Ensure all keys have embeddings
        self._update_embeddings()
        
        # Calculate similarities
        similarities = []
        for key, embedding in self._key_embeddings.items():
            # Cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((key, float(similarity)))
        
        # Sort by similarity (highest first)
        return sorted(similarities, key=lambda x: x[1], reverse=True)
    
    def _select_best_key_with_llm(self, query: str, candidates: List[Tuple[str, float]]) -> Optional[str]:
        """
        Use LLM to select the best matching key from candidates.
        
        Args:
            query: The query string (key not found in dictionary)
            candidates: List of (key, similarity_score) tuples
            
        Returns:
            Selected key or None if no suitable match
        """
        if not candidates:
            return None
            
        # Format candidate keys with their similarity scores
        candidate_text = "\n".join([
            f"- '{key}' (similarity: {score:.4f})" 
            for key, score in candidates
        ])
        
        prompt = f"""
        I'm looking for a key in a dictionary that best matches: '{query}'
        
        Here are the candidate keys with their similarity scores:
        {candidate_text}
        
        Please select the best matching key from the candidates, or respond with "None" if none of them are a good match.
        Only respond with the exact key text or "None", nothing else.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that selects the best matching dictionary key."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=100
            )
            
            selected_key = response.choices[0].message.content.strip().strip("'\"")
            
            # Check if the selected key is actually in our candidates
            candidate_keys = [key for key, _ in candidates]
            if selected_key == "None":
                return None
            elif selected_key in candidate_keys:
                return selected_key
            else:
                # If LLM returned something not in our candidates, use the top similarity match
                logger.warning(f"LLM returned key '{selected_key}' not in candidates, using top similarity match instead")
                return candidates[0][0]
                
        except Exception as e:
            logger.error(f"Error using LLM to select key: {e}")
            # Fallback to top similarity match
            return candidates[0][0] if candidates else None
    
    def __getitem__(self, key: Any) -> Any:
        """
        Get an item from the dictionary, with fuzzy key matching if exact key not found.
        """
        # Try exact match first (standard dictionary behavior)
        try:
            return super().__getitem__(key)
        except KeyError:
            # Only attempt fuzzy matching for string keys
            if not isinstance(key, str):
                raise KeyError(key)
                
            # Find similar keys
            similar_keys = self._find_similar_keys(key)
            
            # Filter by similarity threshold and take top k
            candidates = [(k, s) for k, s in similar_keys if s >= self.similarity_threshold][:self.top_k]
            
            if not candidates:
                raise KeyError(key)
                
            # Use LLM to select best key
            selected_key = self._select_best_key_with_llm(key, candidates)
            
            if selected_key is None:
                raise KeyError(key)
                
            logger.info(f"Fuzzy matched '{key}' to '{selected_key}'")
            return super().__getitem__(selected_key)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        """Set an item in the dictionary and update embeddings if needed."""
        super().__setitem__(key, value)
        
        # Update embedding for the new key if it's a string
        if isinstance(key, str) and key not in self._key_embeddings:
            try:
                self._key_embeddings[key] = self._get_embedding(key)
            except Exception as e:
                logger.error(f"Error updating embedding for new key '{key}': {e}")
                # Continue without embedding - will be retried on next access
    
    def __delitem__(self, key: Any) -> None:
        """Delete an item from the dictionary and its embedding."""
        super().__delitem__(key)
        if key in self._key_embeddings:
            del self._key_embeddings[key]
    
    def clear(self) -> None:
        """Clear the dictionary and embeddings cache."""
        super().clear()
        self._key_embeddings.clear()
    
    def update(self, *args, **kwargs) -> None:
        """Update the dictionary and refresh embeddings."""
        super().update(*args, **kwargs)
        self._update_embeddings() 