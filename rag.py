import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List

class TravelRAG:
    def __init__(self, data_path="data/travel_knowledge.txt"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.index = None
        self.load_data(data_path)
        
    def load_data(self, data_path):
        """Load travel knowledge from text file
        
        Args:
            data_path (str): Path to the text file
        """
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split into chunks
                self.documents = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        else:
            # Fallback data if file doesn't exist
            self.documents = [
                "Tokyo is known for its temples, modern architecture, and incredible food scene.",
                "Best time to visit Kyoto is during cherry blossom season in spring.",
                "Shibuya Crossing is one of the busiest intersections in the world.",
                "Ramen originated in China but became a Japanese staple food.",
                "Mount Fuji is visible from Tokyo on clear days and is a UNESCO World Heritage site."
            ]
        
        # embeddings and FAISS index
        embeddings = self.model.encode(self.documents)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings.astype('float32'))
    
    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Search for relevant documents
        
        Args:
            query (str): Query to search for
            top_k (int, optional): Number of top results to return. Defaults to 3.
        
        Returns:
            List[str]: List of relevant documents
        """
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        return [self.documents[i] for i in indices[0]]