# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Database Setup
```bash
# Initial database setup (required before first run)
poetry run seed-db

# Reset database (WARNING: deletes all data)
poetry run reset-db
```

### Running the Application
```bash
# Main application
poetry run python src/gent_disagreement_processor/main.py
```

### Dependency Management
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add <package>

# Add development dependency
poetry add --group dev <package>
```

## Architecture

This is a **podcast transcript processing pipeline** for "A Gentleman's Disagreement" that:
1. Transcribes audio files using Deepgram API
2. Formats and structures transcript segments
3. Generates embeddings using OpenAI API
4. Stores embeddings in PostgreSQL with pgvector for RAG (Retrieval-Augmented Generation)

### Core Services Architecture

The application follows a modular service-oriented design with these key components:

- **AudioTranscriber**: Handles audio-to-text conversion via Deepgram API
- **TranscriptFormatter**: Structures raw transcript data into segments
- **TranscriptExporter**: Exports formatted segments to JSON files
- **DatabaseManager**: Manages PostgreSQL connections and pgvector storage
- **EmbeddingService**: Generates text embeddings via OpenAI API

### Data Flow

1. Raw audio files (`*.mp3`) → AudioTranscriber → Raw JSON transcripts
2. Raw transcripts → TranscriptFormatter → Structured segments
3. Structured segments → TranscriptExporter → Processed JSON files
4. Processed segments → EmbeddingService → Vector embeddings
5. Embeddings → DatabaseManager → PostgreSQL with pgvector

### Directory Structure

- `src/gent_disagreement_processor/`
  - `core/`: Service classes (transcription, embeddings, database)
  - `models/`: Data models (segments, summaries)
  - `utils/`: Helper functions (data loading)
  - `data/`: Transcript storage
    - `raw/transcripts/`: Deepgram API output
    - `processed/transcripts/`: Formatted segments
- `scripts/`: Database management (seed, reset)
  - `migrations/`: SQL schema definitions

## Environment Variables

Required in `.env` file:
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=<your_password>
DB_NAME=gent_disagreement

# APIs
OPENAI_API_KEY=<your_key>
DEEPGRAM_API_KEY=<your_key>
```

## Database Schema

The application uses PostgreSQL with pgvector extension for embedding storage. Key tables:
- `episodes`: Podcast episode metadata
- `segments`: Transcript segments with embeddings (vector column)

Run migrations via `poetry run seed-db` which executes SQL files in `scripts/migrations/`.