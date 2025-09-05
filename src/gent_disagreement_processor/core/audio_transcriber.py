import os
import traceback
from pathlib import Path
from typing import Optional

from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv


class AudioTranscriber:
    """Handles transcript generation."""

    def __init__(self):
        load_dotenv()

        # Configuration - File paths using pathlib
        # Get the project root directory (4 levels up from this file)
        project_root = Path(__file__).parent.parent.parent.parent
        self.audio_dir = (
            project_root
            / "src"
            / "gent_disagreement_processor"
            / "data"
            / "raw"
            / "audio"
        )
        self.output_dir = (
            project_root
            / "src"
            / "gent_disagreement_processor"
            / "data"
            / "raw"
            / "transcripts"
        )

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configuration - Deepgram settings
        self.model = "nova-3"
        self.language = "en"
        self.transcription_options = PrerecordedOptions(
            model=self.model,
            language=self.language,
            smart_format=True,
            punctuate=True,
            paragraphs=True,
            diarize=True,
            filler_words=False,
        )

    def _validate_audio_file(self, file_path: Path) -> None:
        """Validate that the audio file exists and is accessible.

        Args:
            file_path: Path to the audio file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        print(f"Audio file validation passed: {file_path}")

    def _create_deepgram_client(self) -> DeepgramClient:
        """Create and return a Deepgram client.

        Returns:
            Configured DeepgramClient instance

        Raises:
            ValueError: If API key is not found
        """
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables")

        client = DeepgramClient(api_key)
        print("Deepgram client created successfully")
        return client

    def _transcribe_audio_file(
        self, client: DeepgramClient, audio_file_path: Path
    ) -> any:
        """Transcribe the audio file using Deepgram API.

        Args:
            client: DeepgramClient instance
            audio_file_path: Path to the audio file

        Returns:
            Deepgram API response object
        """
        print(f"Transcribing file: {audio_file_path}")

        with open(audio_file_path, "rb") as audio_file:
            response = client.listen.rest.v("1").transcribe_file(
                {"buffer": audio_file},
                self.transcription_options,
            )

        print("Transcription API call completed")
        return response

    def _save_transcript(self, response: any, base_file_name: str) -> Path:
        """Save the transcript response to a JSON file.

        Args:
            response: Deepgram API response object
            base_file_name: Base name for the output file (without extension)

        Returns:
            Path to the saved transcript file
        """
        output_path = self.output_dir / f"{base_file_name}.json"

        with open(output_path, "w") as f:
            f.write(response.to_json(indent=4))

        print(f"Transcript saved to: {output_path}")
        return output_path

    def generate_transcript(self, file_name: str) -> Optional[str]:
        """Generate a transcript from a local audio file.

        Args:
            file_name: Name of the audio file to transcribe

        Returns:
            Path to the saved transcript file on success, None on failure
        """
        audio_file_path = self.audio_dir / file_name

        try:
            print(f"Starting transcription of: {file_name}")

            # Validate input file
            self._validate_audio_file(audio_file_path)

            # Create Deepgram client
            deepgram_client = self._create_deepgram_client()

            # Transcribe the audio file
            response = self._transcribe_audio_file(deepgram_client, audio_file_path)

            # Save the transcript
            base_file_name = audio_file_path.stem
            output_path = self._save_transcript(response, base_file_name)

            print(f"Transcription completed successfully! Output: {output_path}")
            return str(output_path)

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
