import os
import traceback
from pathlib import Path
from typing import Any, Optional

from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv


class AudioTranscriber:
    """Handles transcript generation from audio files using Deepgram API."""

    def __init__(self):
        load_dotenv()

        # Load and validate API key once during initialization
        self.api_key: str = self._load_and_validate_api_key()

        audio_dir = os.getenv("AUDIO_TRANSCRIBER_AUDIO_DIR")
        self.audio_dir: Path = Path(audio_dir).resolve()

        output_dir = os.getenv("AUDIO_TRANSCRIBER_OUTPUT_DIR")
        self.output_dir: Path = Path(output_dir).resolve()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configuration - Deepgram settings
        self.model: str = "nova-3"
        self.language: str = "en"
        self.transcription_options: PrerecordedOptions = PrerecordedOptions(
            model=self.model,
            language=self.language,
            smart_format=True,
            punctuate=True,
            paragraphs=True,
            diarize=True,
            filler_words=False,
        )

    def _load_and_validate_api_key(self) -> str:
        """Load and validate the Deepgram API key from environment variables.

        Returns:
            str: Validated API key

        Raises:
            ValueError: If API key is not found or invalid
        """
        api_key: Optional[str] = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables")

        # Basic validation - API key should not be empty and should have reasonable length
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY is empty")

        if len(api_key) < 10:
            raise ValueError("DEEPGRAM_API_KEY appears to be invalid (too short)")

        return api_key

    def _validate_audio_file(self, file_path: Path) -> None:
        """Validate that the audio file exists and is accessible.

        Args:
            file_path (Path): Path to the audio file to validate

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

    def _create_deepgram_client(self) -> DeepgramClient:
        """Create and return a Deepgram client.

        Returns:
            Configured DeepgramClient instance

        Raises:
            RuntimeError: If client creation fails
        """
        try:
            client = DeepgramClient(self.api_key)
            return client
        except Exception as e:
            raise RuntimeError(f"Failed to create Deepgram client: {e}") from e

    def _transcribe_audio_file(
        self, client: DeepgramClient, audio_file_path: Path
    ) -> Any:
        """Transcribe the audio file using Deepgram API.

        Args:
            client: DeepgramClient instance
            audio_file_path: Path to the audio file

        Returns:
            Deepgram API response object
        """

        with open(audio_file_path, "rb") as audio_file:
            response = client.listen.rest.v("1").transcribe_file(
                {"buffer": audio_file},
                self.transcription_options,
            )

        return response

    def _save_transcript(self, response: Any, base_file_name: str) -> Path:
        """Save the transcript response to a JSON file.

        Args:
            response: Deepgram API response object
            base_file_name: Base name for the output file (without extension)

        Returns:
            Path to the saved transcript file
        """
        output_path: Path = self.output_dir / f"{base_file_name}.json"

        with open(output_path, "w") as f:
            f.write(response.to_json(indent=4))

        return output_path

    def generate_transcript(self, file_name: str) -> Optional[Path]:
        """Generate a transcript from a local audio file.

        Args:
            file_name: Name of the audio file to transcribe

        Returns:
            Path to the saved transcript file on success, None on failure
        """
        audio_file_path = self.audio_dir / file_name

        try:

            # Validate input file
            self._validate_audio_file(audio_file_path)

            # Create Deepgram client
            deepgram_client = self._create_deepgram_client()

            # Transcribe the audio file
            response = self._transcribe_audio_file(deepgram_client, audio_file_path)

            # Save the transcript
            base_file_name = audio_file_path.stem
            output_path = self._save_transcript(response, base_file_name)

            return output_path

        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return None
        except ValueError as e:
            print(f"Configuration error: {e}")
            return None
        except Exception as e:
            print(f"Transcription failed for {file_name}: {e}")
            traceback.print_exc()
            return None
