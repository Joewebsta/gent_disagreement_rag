"""Comprehensive unit tests for AudioTranscriber class."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from gent_disagreement_processor.core import AudioTranscriber


class TestAudioTranscriber:
    """Test suite for AudioTranscriber functionality."""

    @pytest.fixture
    def valid_env_vars(self, monkeypatch, tmp_path):
        """Set up valid test environment variables."""
        audio_dir = tmp_path / "audio"
        output_dir = tmp_path / "output"
        audio_dir.mkdir()
        output_dir.mkdir()

        monkeypatch.setenv("DEEPGRAM_API_KEY", "valid-api-key-1234567890")
        monkeypatch.setenv("AUDIO_TRANSCRIBER_AUDIO_DIR", str(audio_dir))
        monkeypatch.setenv("AUDIO_TRANSCRIBER_OUTPUT_DIR", str(output_dir))
        return {"audio_dir": audio_dir, "output_dir": output_dir}

    @pytest.fixture
    def mock_deepgram_response(self):
        """Mock Deepgram API response."""
        mock_response = MagicMock()
        mock_response.to_json.return_value = json.dumps(
            {
                "metadata": {"request_id": "test-123", "duration": 120.5},
                "results": {
                    "channels": [
                        {
                            "alternatives": [
                                {
                                    "transcript": "Hello world test transcript",
                                    "confidence": 0.95,
                                    "paragraphs": {
                                        "paragraphs": [
                                            {
                                                "speaker": "0",
                                                "sentences": [
                                                    {
                                                        "text": "Hello world test transcript"
                                                    }
                                                ],
                                            }
                                        ]
                                    },
                                }
                            ]
                        }
                    ]
                },
            }
        )
        return mock_response

    # ===== INITIALIZATION TESTS =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_initialization_success(self, mock_load_dotenv, valid_env_vars):
        """Test successful AudioTranscriber initialization."""
        transcriber = AudioTranscriber()

        assert transcriber.api_key == "valid-api-key-1234567890"
        assert transcriber.model == "nova-3"
        assert transcriber.language == "en"
        assert transcriber.audio_dir == valid_env_vars["audio_dir"]
        assert transcriber.output_dir == valid_env_vars["output_dir"]
        mock_load_dotenv.assert_called_once()

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_initialization_creates_output_directory(
        self, mock_load_dotenv, monkeypatch, tmp_path
    ):
        """Test that initialization creates output directory if it doesn't exist."""
        audio_dir = tmp_path / "audio"
        output_dir = tmp_path / "output_new"  # This directory doesn't exist
        audio_dir.mkdir()

        monkeypatch.setenv("DEEPGRAM_API_KEY", "valid-api-key-1234567890")
        monkeypatch.setenv("AUDIO_TRANSCRIBER_AUDIO_DIR", str(audio_dir))
        monkeypatch.setenv("AUDIO_TRANSCRIBER_OUTPUT_DIR", str(output_dir))

        transcriber = AudioTranscriber()

        assert output_dir.exists()
        assert transcriber.output_dir == output_dir

    # ===== API KEY VALIDATION TESTS =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_missing_api_key_raises_error(
        self, mock_load_dotenv, monkeypatch, tmp_path
    ):
        """Test that missing API key raises ValueError."""
        audio_dir = tmp_path / "audio"
        output_dir = tmp_path / "output"
        audio_dir.mkdir()
        output_dir.mkdir()

        monkeypatch.delenv("DEEPGRAM_API_KEY", raising=False)
        monkeypatch.setenv("AUDIO_TRANSCRIBER_AUDIO_DIR", str(audio_dir))
        monkeypatch.setenv("AUDIO_TRANSCRIBER_OUTPUT_DIR", str(output_dir))

        with pytest.raises(
            ValueError, match="DEEPGRAM_API_KEY not found in environment variables"
        ):
            AudioTranscriber()

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_empty_api_key_raises_error(self, mock_load_dotenv, monkeypatch, tmp_path):
        """Test that empty API key raises ValueError."""
        audio_dir = tmp_path / "audio"
        output_dir = tmp_path / "output"
        audio_dir.mkdir()
        output_dir.mkdir()

        monkeypatch.setenv("DEEPGRAM_API_KEY", "   ")  # Whitespace only
        monkeypatch.setenv("AUDIO_TRANSCRIBER_AUDIO_DIR", str(audio_dir))
        monkeypatch.setenv("AUDIO_TRANSCRIBER_OUTPUT_DIR", str(output_dir))

        with pytest.raises(ValueError, match="DEEPGRAM_API_KEY is empty"):
            AudioTranscriber()

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_short_api_key_raises_error(self, mock_load_dotenv, monkeypatch, tmp_path):
        """Test that too-short API key raises ValueError."""
        audio_dir = tmp_path / "audio"
        output_dir = tmp_path / "output"
        audio_dir.mkdir()
        output_dir.mkdir()

        monkeypatch.setenv("DEEPGRAM_API_KEY", "short")  # Less than 10 characters
        monkeypatch.setenv("AUDIO_TRANSCRIBER_AUDIO_DIR", str(audio_dir))
        monkeypatch.setenv("AUDIO_TRANSCRIBER_OUTPUT_DIR", str(output_dir))

        with pytest.raises(
            ValueError, match="DEEPGRAM_API_KEY appears to be invalid \\(too short\\)"
        ):
            AudioTranscriber()

    # ===== FILE VALIDATION TESTS =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_validate_audio_file_exists(self, mock_load_dotenv, valid_env_vars):
        """Test file validation passes when file exists."""
        transcriber = AudioTranscriber()

        # Create a test audio file
        test_audio_file = valid_env_vars["audio_dir"] / "test.mp3"
        test_audio_file.write_bytes(b"fake audio content")

        # Should not raise any exception
        transcriber._validate_audio_file(test_audio_file)

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_validate_audio_file_not_found(self, mock_load_dotenv, valid_env_vars):
        """Test file validation raises error when file doesn't exist."""
        transcriber = AudioTranscriber()

        missing_file = valid_env_vars["audio_dir"] / "missing.mp3"

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            transcriber._validate_audio_file(missing_file)

    # ===== DEEPGRAM CLIENT CREATION TESTS =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("gent_disagreement_processor.core.audio_transcriber.DeepgramClient")
    def test_create_deepgram_client_success(
        self, mock_deepgram_client, mock_load_dotenv, valid_env_vars
    ):
        """Test successful Deepgram client creation."""
        mock_client_instance = MagicMock()
        mock_deepgram_client.return_value = mock_client_instance

        transcriber = AudioTranscriber()
        client = transcriber._create_deepgram_client()

        mock_deepgram_client.assert_called_with("valid-api-key-1234567890")
        assert client == mock_client_instance

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("gent_disagreement_processor.core.audio_transcriber.DeepgramClient")
    def test_create_deepgram_client_failure(
        self, mock_deepgram_client, mock_load_dotenv, valid_env_vars
    ):
        """Test Deepgram client creation failure handling."""
        mock_deepgram_client.side_effect = Exception("Client creation failed")

        transcriber = AudioTranscriber()

        with pytest.raises(RuntimeError, match="Failed to create Deepgram client"):
            transcriber._create_deepgram_client()

    # ===== AUDIO TRANSCRIPTION TESTS =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake audio content")
    def test_transcribe_audio_file_success(
        self, mock_file_open, mock_load_dotenv, valid_env_vars, mock_deepgram_response
    ):
        """Test successful audio transcription."""
        transcriber = AudioTranscriber()

        # Create test audio file
        test_audio_file = valid_env_vars["audio_dir"] / "test.mp3"
        test_audio_file.write_bytes(b"fake audio content")

        # Mock client
        mock_client = MagicMock()
        mock_client.listen.rest.v.return_value.transcribe_file.return_value = (
            mock_deepgram_response
        )

        result = transcriber._transcribe_audio_file(mock_client, test_audio_file)

        assert result == mock_deepgram_response
        mock_client.listen.rest.v.assert_called_with("1")
        mock_client.listen.rest.v.return_value.transcribe_file.assert_called_once()

    # ===== TRANSCRIPT SAVING TESTS =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_transcript_success(
        self, mock_file_open, mock_load_dotenv, valid_env_vars, mock_deepgram_response
    ):
        """Test successful transcript saving."""
        transcriber = AudioTranscriber()

        output_path = transcriber._save_transcript(
            mock_deepgram_response, "test_episode"
        )

        expected_path = valid_env_vars["output_dir"] / "test_episode.json"
        assert output_path == expected_path

        # Verify file was opened for writing
        mock_file_open.assert_called_with(expected_path, "w")

        # Verify JSON content was written
        mock_deepgram_response.to_json.assert_called_with(indent=4)

    # ===== INTEGRATION TESTS (generate_transcript) =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("gent_disagreement_processor.core.audio_transcriber.DeepgramClient")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake audio content")
    def test_generate_transcript_complete_success(
        self,
        mock_file_open,
        mock_deepgram_client,
        mock_load_dotenv,
        valid_env_vars,
        mock_deepgram_response,
    ):
        """Test complete successful transcript generation workflow."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_deepgram_client.return_value = mock_client_instance
        mock_client_instance.listen.rest.v.return_value.transcribe_file.return_value = (
            mock_deepgram_response
        )

        # Create test audio file
        test_audio_file = valid_env_vars["audio_dir"] / "test.mp3"
        test_audio_file.write_bytes(b"fake audio content")

        transcriber = AudioTranscriber()
        result = transcriber.generate_transcript("test.mp3")

        # Verify successful completion
        expected_output = valid_env_vars["output_dir"] / "test.json"
        assert result == expected_output

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_generate_transcript_file_not_found(self, mock_load_dotenv, valid_env_vars):
        """Test generate_transcript handles missing audio file gracefully."""
        transcriber = AudioTranscriber()

        result = transcriber.generate_transcript("nonexistent.mp3")

        assert result is None

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("gent_disagreement_processor.core.audio_transcriber.DeepgramClient")
    def test_generate_transcript_client_creation_failure(
        self, mock_deepgram_client, mock_load_dotenv, valid_env_vars
    ):
        """Test generate_transcript handles client creation failure gracefully."""
        mock_deepgram_client.side_effect = Exception("Client creation failed")

        # Create test audio file
        test_audio_file = valid_env_vars["audio_dir"] / "test.mp3"
        test_audio_file.write_bytes(b"fake audio content")

        transcriber = AudioTranscriber()
        result = transcriber.generate_transcript("test.mp3")

        assert result is None

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("gent_disagreement_processor.core.audio_transcriber.DeepgramClient")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake audio content")
    def test_generate_transcript_api_failure(
        self, mock_file_open, mock_deepgram_client, mock_load_dotenv, valid_env_vars
    ):
        """Test generate_transcript handles API failure gracefully."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_deepgram_client.return_value = mock_client_instance
        mock_client_instance.listen.rest.v.return_value.transcribe_file.side_effect = (
            Exception("API Error")
        )

        # Create test audio file
        test_audio_file = valid_env_vars["audio_dir"] / "test.mp3"
        test_audio_file.write_bytes(b"fake audio content")

        transcriber = AudioTranscriber()
        result = transcriber.generate_transcript("test.mp3")

        assert result is None

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    @patch("gent_disagreement_processor.core.audio_transcriber.DeepgramClient")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake audio content")
    def test_generate_transcript_save_failure(
        self,
        mock_file_open,
        mock_deepgram_client,
        mock_load_dotenv,
        valid_env_vars,
        mock_deepgram_response,
    ):
        """Test generate_transcript handles save failure gracefully."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_deepgram_client.return_value = mock_client_instance
        mock_client_instance.listen.rest.v.return_value.transcribe_file.return_value = (
            mock_deepgram_response
        )

        # Make file writing fail
        mock_file_open.side_effect = [
            mock_open(
                read_data=b"fake audio content"
            ).return_value,  # For reading audio
            Exception("Write failed"),  # For writing transcript
        ]

        # Create test audio file
        test_audio_file = valid_env_vars["audio_dir"] / "test.mp3"
        test_audio_file.write_bytes(b"fake audio content")

        transcriber = AudioTranscriber()
        result = transcriber.generate_transcript("test.mp3")

        assert result is None

    # ===== CONFIGURATION TESTS =====

    @patch("gent_disagreement_processor.core.audio_transcriber.load_dotenv")
    def test_transcription_options_configuration(
        self, mock_load_dotenv, valid_env_vars
    ):
        """Test that transcription options are configured correctly."""
        transcriber = AudioTranscriber()

        options = transcriber.transcription_options
        assert options.model == "nova-3"
        assert options.language == "en"
        assert options.smart_format is True
        assert options.punctuate is True
        assert options.paragraphs is True
        assert options.diarize is True
        assert options.filler_words is False
