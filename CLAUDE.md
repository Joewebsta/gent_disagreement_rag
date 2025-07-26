# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) application for analyzing disagreements in "A Gentleman's Disagreement" transcript data. The system processes audio transcripts, creates embeddings, and stores them in PostgreSQL with vector search capabilities.

## Architecture

The application follows a pipeline-based architecture with distinct processing stages:

### Core Processing Pipeline (`src/gent_disagreement_rag/core/`)
- **AudioTranscriptProcessor**: Main orchestrator that coordinates the entire processing pipeline
- **DataFormatter**: Formats raw transcript segments
- **SegmentProcessor**: Processes segments for embedding preparation
- **SpeakerSummarizer**: Creates summaries for each speaker
- **Preprocessor/Normalizer**: Data preprocessing utilities

### Data Layer (`src/gent_disagreement_rag/data/`)
- **raw/**: Contains raw transcript data
- **processed/**: Stores processed segments ready for embedding generation
- Models define the data structures for segments and summaries

### Database Layer
- **DatabaseManager**: Handles PostgreSQL connections and vector database operations
- Uses pgvector extension for storing and querying embeddings
- Table: `transcript_segments` with speaker, text, and vector(1536) embedding columns

### Utilities (`src/gent_disagreement_rag/utils/`)
- **DataExporter**: Exports processed data
- **StatisticsReporter**: Generates processing statistics
- **Categorizer/Chunker**: Text processing utilities

## Development Commands

### Environment Setup
```bash
poetry install          # Install dependencies
poetry shell            # Activate virtual environment
```

### Running the Application
```bash
python main.py          # Run from project root
# OR
python -m src.gent_disagreement_rag.main  # Run as module
```

### Database Requirements
- PostgreSQL with pgvector extension
- Environment variables needed:
  - `OPENAI_API_KEY`: OpenAI API key for embeddings
  - `DB_HOST`: Database host (default: localhost)
  - `DB_PORT`: Database port (default: 5432)
  - `DB_USER`: Database user (default: postgres)
  - `DB_PASSWORD`: Database password (required)
  - `DB_NAME`: Database name (default: gent_disagreement)

## Key Dependencies
- **OpenAI**: Text embedding generation (text-embedding-3-small model)
- **psycopg2**: PostgreSQL database connectivity
- **python-dotenv**: Environment variable management

## Current Processing Flow
1. Load raw transcript data
2. Format and normalize segments using AudioTranscriptProcessor
3. Generate OpenAI embeddings for each segment
4. Store embeddings in PostgreSQL with vector search capability
5. Export processed data and generate statistics

## Entry Points
- `main.py`: Root entry point that imports from src module
- `src/gent_disagreement_rag/main.py`: Main application logic with embedding generation