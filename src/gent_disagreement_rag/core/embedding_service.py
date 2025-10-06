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

    def generate_embeddings_batched(self, text_array: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in one API call."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small", input=text_array
        )
        return [item.embedding for item in response.data]

    def generate_embeddings(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for all segments using batch API call (efficient)."""
        try:
            # Extract all text from segments
            segment_texts = [segment["text"] for segment in segments]

            # Generate all embeddings in one API call
            embeddings_batch = self.generate_embeddings_batched(segment_texts)

            # Map embeddings back to segments
            segments_with_embeddings = []
            for original_segment, embedding_vector in zip(segments, embeddings_batch):
                segments_with_embeddings.append(
                    {
                        "speaker": original_segment["speaker"],
                        "text": original_segment["text"],
                        "embedding": embedding_vector,
                    }
                )

            print("All embeddings generated successfully!")
            return segments_with_embeddings
        except Exception as e:
            print("Error generating embeddings:", e)
            raise

    def generate_embeddings_sequential(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate embeddings one-by-one for each segment (fallback/debugging)."""
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
