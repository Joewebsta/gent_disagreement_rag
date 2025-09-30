# Gent Disagreement RAG

A production-ready podcast transcript processing pipeline that transcribes audio files, generates embeddings, and stores them in PostgreSQL with pgvector for Retrieval-Augmented Generation (RAG) applications.

## Overview

This application processes podcast episodes from "A Gentleman's Disagreement" by:
1. Transcribing audio files using Deepgram's speech-to-text API
2. Formatting and structuring transcript segments with speaker identification
3. Generating vector embeddings using OpenAI's embedding models
4. Storing embeddings in PostgreSQL with pgvector for semantic search and RAG

## Features

- **Audio Transcription**: High-quality speech-to-text conversion with speaker diarization using Deepgram Nova-3
- **Transcript Formatting**: Structured segmentation with speaker attribution and metadata
- **Vector Embeddings**: Semantic embeddings generated via OpenAI's text-embedding-3-small model
- **Vector Storage**: PostgreSQL with pgvector extension for efficient similarity search
- **Modular Architecture**: Clean separation of concerns with service-oriented design
- **Error Handling**: Robust validation and error handling throughout the pipeline
- **Test Coverage**: Comprehensive unit, integration, and end-to-end tests

## Architecture

### System Components

```
Audio Files (*.mp3)
        |
        v
AudioTranscriber -----> Deepgram API
        |
        v
TranscriptFormatter
        |
        v
TranscriptExporter
        |
        v
EmbeddingService -----> OpenAI API
        |
        v
DatabaseManager -----> PostgreSQL + pgvector
```

### Data Flow

1. **Raw Audio** (`*.mp3`) → **AudioTranscriber** → Raw JSON transcripts
2. **Raw Transcripts** → **TranscriptFormatter** → Structured segments
3. **Structured Segments** → **TranscriptExporter** → Processed JSON files
4. **Processed Segments** → **EmbeddingService** → Vector embeddings
5. **Embeddings** → **DatabaseManager** → PostgreSQL storage with pgvector

## Technology Stack

- **Python**: ≥3.11
- **Deepgram SDK**: Speech-to-text transcription with diarization
- **OpenAI API**: Text embedding generation (text-embedding-3-small)
- **PostgreSQL**: Primary database with pgvector extension
- **Poetry**: Dependency management and packaging
- **pytest**: Testing framework with mocking and async support

## Prerequisites

- Python 3.11 or higher
- PostgreSQL with pgvector extension installed
- Poetry for dependency management
- API keys for:
  - Deepgram (for audio transcription)
  - OpenAI (for embeddings)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd gent_disagreement_rag
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=gent_disagreement

# API Keys
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key

# Audio Transcriber Configuration
AUDIO_TRANSCRIBER_AUDIO_DIR=./data/audio
AUDIO_TRANSCRIBER_OUTPUT_DIR=./data/raw/transcripts
```

### 4. Set Up PostgreSQL

Ensure PostgreSQL is running and the pgvector extension is available:

```bash
# Install pgvector (macOS with Homebrew)
brew install pgvector

# Or follow instructions at https://github.com/pgvector/pgvector
```

### 5. Initialize the Database

Run the database setup script to create tables and seed initial data:

```bash
poetry run seed-db
```

This will:
- Create the database schema
- Enable the pgvector extension
- Create `episodes` and `transcript_segments` tables
- Seed initial episode data

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `your_password` |
| `DB_NAME` | Database name | `gent_disagreement` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `DEEPGRAM_API_KEY` | Deepgram API key | `your_key` |
| `AUDIO_TRANSCRIBER_AUDIO_DIR` | Audio files directory | `./data/audio` |
| `AUDIO_TRANSCRIBER_OUTPUT_DIR` | Transcript output directory | `./data/raw/transcripts` |

## Usage

### Running the Main Application

```bash
poetry run python src/gent_disagreement_rag/main.py
```

The application will:
1. Process configured episodes (AGD-180, AGD-181, AGD-182)
2. Transcribe audio files via Deepgram
3. Format and structure transcripts
4. Generate embeddings via OpenAI
5. Store embeddings in PostgreSQL

### Database Management

#### Reset Database (⚠️ Deletes All Data)

```bash
poetry run reset-db
```

#### Re-seed Database

```bash
poetry run seed-db
```

### Adding New Episodes

Edit the `episodes` list in `src/gent_disagreement_rag/main.py`:

```python
episodes = [
    {"episode_id": 1, "file_name": "AGD-180.mp3"},
    {"episode_id": 2, "file_name": "AGD-181.mp3"},
    # Add more episodes here
]
```

## Project Structure

```
gent_disagreement_rag/
├── src/gent_disagreement_rag/
│   ├── core/                      # Core service classes
│   │   ├── audio_transcriber.py   # Deepgram transcription
│   │   ├── transcript_formatter.py # Segment formatting
│   │   ├── transcript_exporter.py # JSON export
│   │   ├── embedding_service.py   # OpenAI embeddings
│   │   └── database_manager.py    # PostgreSQL + pgvector
│   ├── models/                    # Data models
│   │   ├── segments.py            # Segment definitions
│   │   └── summaries.py           # Summary models
│   ├── utils/                     # Helper utilities
│   │   └── data_loader.py         # Data loading functions
│   ├── data/                      # Data storage
│   │   ├── audio/                 # Source audio files
│   │   ├── raw/transcripts/       # Deepgram output
│   │   └── processed/transcripts/ # Formatted segments
│   └── main.py                    # Application entry point
├── scripts/                       # Database management
│   ├── seed_database.py           # Database initialization
│   ├── reset_database.py          # Database reset
│   └── migrations/                # SQL migrations
│       ├── 001_initial_schema.sql # Schema creation
│       └── 002_seed_episodes.sql  # Initial data
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
├── pyproject.toml                 # Poetry configuration
├── .env                           # Environment variables (not in git)
└── README.md                      # This file
```

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/unit/test_audio_transcriber.py

# Run with verbose output
poetry run pytest -v
```

### Test Structure

- **Unit Tests**: Test individual service classes in isolation with mocked dependencies
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete pipeline workflows

### Adding New Dependencies

```bash
# Production dependency
poetry add <package>

# Development dependency
poetry add --group dev <package>
```

## Database Schema

### Episodes Table

```sql
CREATE TABLE episodes (
    id SERIAL PRIMARY KEY,
    episode_number VARCHAR(20) NOT NULL UNIQUE,
    title TEXT,
    file_name VARCHAR(255),
    date_published DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transcript Segments Table

```sql
CREATE TABLE transcript_segments (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES episodes(id),
    speaker TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding vector(1536)
);
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Joe Webster - joseph.scott.webster@gmail.com

## Acknowledgments

- [Deepgram](https://deepgram.com/) for speech-to-text API
- [OpenAI](https://openai.com/) for embedding generation
- [pgvector](https://github.com/pgvector/pgvector) for PostgreSQL vector extension