# Resume Bullet Points

## Full Stack AI Engineer - Podcast RAG Pipeline

### Primary Bullet Points

• Built end-to-end podcast transcript processing pipeline integrating Deepgram for audio transcription, OpenAI embeddings, and PostgreSQL with pgvector for semantic search capabilities

• Designed modular service-oriented architecture with 5 core services (AudioTranscriber, TranscriptFormatter, EmbeddingService, DatabaseManager, TranscriptExporter) following separation of concerns principles

• Implemented RAG (Retrieval-Augmented Generation) infrastructure by generating and storing vector embeddings of podcast segments in PostgreSQL, enabling semantic search over transcript data

• Developed automated data pipeline processing audio files through transcription, segmentation, embedding generation, and vector database storage with comprehensive error handling

• Engineered PostgreSQL database schema with pgvector extension for efficient similarity search, including migration scripts and database management tooling (seed/reset commands)

• Integrated multiple third-party APIs (Deepgram for speech-to-text, OpenAI for embeddings) with proper credential management and environment configuration

• Built Python CLI application using Poetry for dependency management, featuring custom scripts for database operations and data processing workflows

• Established testing infrastructure with pytest for unit testing core services, ensuring reliability of transcription and data processing pipelines

### Alternative/Supplementary Bullet Points

• Created scalable transcript formatting service that structures raw API output into semantically meaningful segments for embedding generation and retrieval

• Developed JSON-based export system for processed transcripts, enabling data portability and integration with downstream AI/ML workflows

---

## Tips for Customization

- Choose 3-5 bullets that best match the job description
- Lead with bullets emphasizing skills mentioned in the posting (AI/ML, backend, full-stack, databases)
- Quantify impact when possible (e.g., "processing X hours of audio" or "handling Y episodes")
- Adjust technical depth based on role level (junior vs senior positions)