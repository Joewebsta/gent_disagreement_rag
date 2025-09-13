"""Pytest configuration and shared fixtures for the test suite."""

import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from faker import Faker

fake = Faker()


# Database fixtures
@pytest.fixture
def test_db_connection():
    """Mock database connection for testing."""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def clean_db_env(monkeypatch):
    """Set up clean test database environment variables."""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_NAME", "gent_disagreement_test")


# API mocking fixtures
@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings API responses."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Default embedding response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]  # text-embedding-3-small size
        mock_client.embeddings.create.return_value = mock_response

        yield mock_client


@pytest.fixture
def mock_deepgram_client():
    """Mock Deepgram client for transcription testing."""
    with patch('deepgram.DeepgramClient') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Default transcription response structure
        mock_response = {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "paragraphs": {
                                    "paragraphs": [
                                        {
                                            "speaker": "0",
                                            "sentences": [
                                                {"text": "Sample transcribed text."}
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        }

        mock_instance.listen.prerecorded.v.return_value = mock_response
        yield mock_instance


# Data fixtures
@pytest.fixture
def sample_segments():
    """Generate sample transcript segments."""
    return [
        {"speaker": "Ricky Ghoshroy", "text": fake.paragraph()},
        {"speaker": "Brendan Kelly", "text": fake.paragraph()},
        {"speaker": "Ricky Ghoshroy", "text": fake.paragraph()},
    ]


@pytest.fixture
def sample_embeddings(sample_segments):
    """Generate sample embeddings for segments."""
    embeddings = []
    for segment in sample_segments:
        embeddings.append({
            "speaker": segment["speaker"],
            "text": segment["text"],
            "embedding": [fake.random.uniform(-1, 1) for _ in range(1536)]
        })
    return embeddings


@pytest.fixture
def sample_transcript_file(tmp_path):
    """Create a sample transcript JSON file for testing."""
    transcript_data = {
        "results": {
            "channels": [
                {
                    "alternatives": [
                        {
                            "paragraphs": {
                                "paragraphs": [
                                    {
                                        "speaker": "0",
                                        "sentences": [
                                            {"text": "Hello and welcome to the show."},
                                            {"text": "Today we're discussing an interesting topic."}
                                        ]
                                    },
                                    {
                                        "speaker": "1",
                                        "sentences": [
                                            {"text": "Thanks for having me."},
                                            {"text": "I'm excited to be here."}
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    }

    transcript_file = tmp_path / "sample_transcript.json"
    transcript_file.write_text(json.dumps(transcript_data))
    return transcript_file


# Temporary directory fixtures
@pytest.fixture
def temp_audio_dir(tmp_path):
    """Create temporary audio directory for testing."""
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    return audio_dir


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for testing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


# Environment variable fixtures
@pytest.fixture
def test_env_vars(monkeypatch, temp_audio_dir, temp_output_dir):
    """Set up comprehensive test environment variables."""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_NAME", "gent_disagreement_test")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test-deepgram-key")
    monkeypatch.setenv("AUDIO_TRANSCRIBER_AUDIO_DIR", str(temp_audio_dir))
    monkeypatch.setenv("AUDIO_TRANSCRIBER_OUTPUT_DIR", str(temp_output_dir))
    monkeypatch.setenv("TRANSCRIPT_FORMATTER_OUTPUT_DIR", str(temp_output_dir))


# Utility functions for tests
def create_mock_audio_file(audio_dir: Path, filename: str = "test.mp3") -> Path:
    """Create a mock audio file for testing."""
    audio_file = audio_dir / filename
    audio_file.write_bytes(b"fake audio content")
    return audio_file


def assert_valid_embedding(embedding):
    """Assert that an embedding is valid."""
    assert isinstance(embedding, list)
    assert len(embedding) == 1536  # text-embedding-3-small dimension
    assert all(isinstance(x, (int, float)) for x in embedding)