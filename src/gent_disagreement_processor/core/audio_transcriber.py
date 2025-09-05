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

            api_key = os.getenv("DEEPGRAM_API_KEY")
            if not api_key:
                raise ValueError("DEEPGRAM_API_KEY not found in environment variables")

            deepgram = DeepgramClient(api_key)
            print("Deepgram client created successfully")

            # Check if file exists
            if not audio_file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            # Read the local file and transcribe it
            print("Starting transcription...")
            with open(audio_file_path, "rb") as audio_file:
                response = deepgram.listen.rest.v("1").transcribe_file(
                    {"buffer": audio_file},
                    self.transcription_options,
                )

            # Save the response json to the transcripts directory
            # The file name should be the audio file name without the extension
            base_file_name = audio_file_path.stem  # Gets filename without extension
            output_path = self.output_dir / f"{base_file_name}.json"

            with open(output_path, "w") as f:
                f.write(response.to_json(indent=4))

            print("Transcription completed successfully!")
            return str(output_path)  # Convert Path object to string for return

        except Exception as e:
            print(f"Exception: {e}")
            traceback.print_exc()
            return None  # Return None instead of empty string on failure
