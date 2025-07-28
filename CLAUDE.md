# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) application for processing "A Gentleman's Disagreement" podcast transcript data. The system processes audio transcripts, creates embeddings, stores them in PostgreSQL with vector search capabilities, and provides an interactive chat interface for querying the transcript data.

## Architecture

The application follows a pipeline-based architecture with distinct processing stages and now includes a complete RAG implementation:

### Core Processing Pipeline (`src/gent_disagreement_processor/core/`)
- **AudioTranscriptProcessor**: Main orchestrator that coordinates the entire processing pipeline
- **DatabaseManager**: Handles PostgreSQL connections and vector database operations
- **EmbeddingService**: Generates and manages OpenAI text embeddings
- **VectorSearch**: Performs similarity search operations on stored embeddings
- **RAGService**: Orchestrates the retrieval-augmented generation process
- **ChatManager**: Interactive chat interface for user queries
- **DataFormatter/Preprocessor/Normalizer**: Data processing utilities
- **SegmentProcessor**: Processes segments for embedding preparation
- **SpeakerSummarizer**: Creates summaries for each speaker

### Data Layer (`src/gent_disagreement_processor/data/`)
- **raw/**: Contains raw transcript data
- **processed/**: Stores processed segments ready for embedding generation
- **Models**: Define data structures for segments and summaries

### Database Layer
- **DatabaseManager**: Handles PostgreSQL connections and vector database operations
- Uses pgvector extension for storing and querying embeddings
- Table: `transcript_segments` with speaker, text, and vector(1536) embedding columns
- Supports cosine similarity search with configurable thresholds

### RAG Components
- **VectorSearch**: Handles similarity search with threshold filtering and top-k retrieval
- **RAGService**: Combines search results with OpenAI LLM for contextual responses
- **ChatManager**: Provides interactive command-line interface

### Utilities (`src/gent_disagreement_processor/utils/`)
- **DataExporter**: Exports processed data
- **StatisticsReporter**: Generates processing statistics
- **DataLoader**: Loads processed segments for embedding generation
- **Categorizer/Chunker**: Text processing utilities

## Development Commands

### Environment Setup
```bash
poetry install          # Install dependencies
poetry shell            # Activate virtual environment
```

### Running the Application
```bash
python main.py          # Run interactive chat interface
# OR
python -m src.gent_disagreement_processor.main  # Run as module
```

### Database Requirements
- PostgreSQL with pgvector extension
- Environment variables needed:
  - `OPENAI_API_KEY`: OpenAI API key for embeddings and chat completions
  - `DB_HOST`: Database host (default: localhost)
  - `DB_PORT`: Database port (default: 5432)
  - `DB_USER`: Database user (default: postgres)
  - `DB_PASSWORD`: Database password (required)
  - `DB_NAME`: Database name (default: gent_disagreement)

## Key Dependencies
- **OpenAI**: Text embedding generation (text-embedding-3-small) and chat completions (gpt-4o-mini)
- **psycopg2**: PostgreSQL database connectivity
- **python-dotenv**: Environment variable management

## Current Application Flow
1. **Interactive Mode**: Launches ChatManager for real-time Q&A
2. **Query Processing**: User questions are embedded and searched against transcript segments
3. **Context Retrieval**: Most similar segments are retrieved using vector search
4. **Response Generation**: OpenAI LLM generates responses using retrieved context
5. **Conversational Interface**: Maintains chat session until user exits

## Entry Points
- `main.py`: Root entry point that launches the interactive chat interface
- `src/gent_disagreement_processor/main.py`: Main application logic with ChatManager integration

## Processing Pipeline (Commented Out)
The data processing pipeline components are available but currently commented out in main.py:
1. Load raw transcript data using AudioTranscriptProcessor
2. Setup database with DatabaseManager
3. Generate OpenAI embeddings for processed segments
4. Store embeddings in PostgreSQL with vector search capability