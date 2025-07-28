from typing import List


class TextChunker:
    """Handles text chunking for long segments."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk long text into smaller, overlapping pieces for better embedding.
        """
        words = text.split()

        if len(words) <= self.chunk_size:
            return [text]

        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = " ".join(words[i : i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks
