# Testing Plan for Gent Disagreement Processor

## Overview
This document outlines the comprehensive testing strategy for the podcast transcript processing pipeline.

## Testing Approaches

### 1. Unit Testing - Test Individual Components
Each service class should be tested in isolation:

- **AudioTranscriber**: Mock Deepgram API responses, test error handling, file path validation
- **TranscriptFormatter**: Test parsing logic with sample JSON data, edge cases (empty paragraphs, missing speakers)
- **EmbeddingService**: Mock OpenAI API, test embedding generation, batch processing
- **DatabaseManager**: Test connection handling, embedding storage, transaction rollback on errors
- **TranscriptExporter**: Test file writing, JSON formatting, directory creation

### 2. Integration Testing - Test Component Interactions
Test how services work together:

- Audio file → Transcription → Formatting pipeline
- Formatted segments → Embeddings → Database storage
- Database connection failures and recovery
- API rate limiting and retry logic

### 3. End-to-End Testing - Test Complete Workflow
Test the entire pipeline with sample audio files:

- Process a short test audio file through the complete pipeline
- Verify database contains correct embeddings
- Test with multiple episodes in sequence
- Validate data integrity from audio to database

### 4. External Service Testing
Since you depend on external APIs:

- **Mock Testing**: Use mock responses for Deepgram and OpenAI
- **Contract Testing**: Verify API response formats haven't changed
- **Smoke Tests**: Basic connectivity tests with real APIs (using test credentials)

### 5. Database Testing
- Schema migration testing (seed-db and reset-db scripts)
- Vector similarity search accuracy
- Database constraints and indexes
- Connection pooling and timeouts

### 6. Error Handling & Edge Cases
Test failure scenarios:

- Missing environment variables
- Invalid API keys
- Network timeouts
- Malformed audio files
- Database connection failures
- Partial processing failures (e.g., embedding fails for one segment)

## Implementation Plan

### Phase 1: Setup Testing Infrastructure
1. Install pytest and testing dependencies (pytest-mock, pytest-asyncio, faker)
2. Create test directory structure matching source code
3. Set up test configuration and fixtures
4. Create test database and .env.test file

### Phase 2: Unit Tests
1. Create test_audio_transcriber.py - Mock Deepgram API, test file handling
2. Create test_transcript_formatter.py - Test parsing logic with fixture data
3. Create test_embedding_service.py - Mock OpenAI API responses
4. Create test_database_manager.py - Test with test database
5. Create test_transcript_exporter.py - Test file operations

### Phase 3: Integration Tests
1. Create test_pipeline_integration.py - Test service interactions
2. Test error propagation between services
3. Test transaction rollback scenarios

### Phase 4: End-to-End Tests
1. Create sample test audio file (short clip)
2. Create test_end_to_end.py - Full pipeline test
3. Add database verification helpers

### Phase 5: Test Utilities
1. Create conftest.py with shared fixtures
2. Add mock data generators
3. Create test data fixtures (sample transcripts)
4. Add database cleanup utilities

## Key Testing Principles

- **Use dependency injection** to make services testable
- **Create factory functions** for test data
- **Isolate external dependencies** with mocks
- **Test both happy path and error scenarios**
- **Verify data transformations** at each step
- **Use pytest fixtures** for reusable test setup

## Sample Test Structure

```python
# tests/unit/test_transcript_formatter.py
import pytest
from gent_disagreement_rag.core import TranscriptFormatter

class TestTranscriptFormatter:
    def test_format_segments_with_valid_data(self, sample_transcript_data):
        formatter = TranscriptFormatter()
        segments = formatter.format_segments(sample_transcript_data)
        assert len(segments) > 0
        assert all('speaker' in s and 'text' in s for s in segments)

    def test_format_segments_with_speaker_mapping(self, sample_transcript_data):
        formatter = TranscriptFormatter()
        segments = formatter.format_segments(sample_transcript_data)
        speakers = {s['speaker'] for s in segments}
        assert speakers.issubset({'Ricky Ghoshroy', 'Brendan Kelly'})
```

## Testing Commands

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=gent_disagreement_rag

# Run specific test file
poetry run pytest tests/unit/test_audio_transcriber.py

# Run tests with verbose output
poetry run pytest -v

# Run only unit tests
poetry run pytest tests/unit/

# Run only integration tests
poetry run pytest tests/integration/
```

## Continuous Testing Strategy

1. **Pre-commit hooks**: Run unit tests before commits
2. **CI/CD pipeline**: Run full test suite on push
3. **Nightly tests**: Run end-to-end tests with real APIs
4. **Performance benchmarks**: Track processing times for audio files
5. **Data validation**: Verify embedding quality and database integrity

## Success Criteria

- Unit test coverage > 80%
- All integration tests passing
- End-to-end test completes in < 60 seconds for test audio
- No critical security vulnerabilities
- API mocking reduces test runtime by > 90%