import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv


class EmbeddingService:
    """Handles embedding generation for transcript segments."""

    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_embedding(self, text: str) -> List[float]:
        """Generate a single embedding for the given text."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small", input=text
        )
        return response.data[0].embedding

    def generate_embeddings(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for all segments and return them with segment data."""
        try:
            embeddings = []
            for segment in segments:
                embedding = self.generate_embedding(segment["text"])
                embeddings.append(
                    {
                        "speaker": segment["speaker"],
                        "text": segment["text"],
                        "embedding": embedding,
                    }
                )
            print("All embeddings generated successfully!")
            return embeddings
        except Exception as e:
            print("Error generating embeddings:", e)
            raise
