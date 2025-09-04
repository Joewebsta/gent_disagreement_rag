import os
import traceback
from typing import Optional

from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv


class AudioTranscriber:
    """Handles transcript generation."""

    def __init__(self):
        load_dotenv()

    def generate_transcript(self, file_name: str) -> Optional[str]:
        """Generate a transcript from a local audio file.

        Args:
            file_name: Name of the audio file to transcribe

        Returns:
            Path to the saved transcript file on success, None on failure
        """
        audio_file_path = f"src/gent_disagreement_processor/data/raw/audio/{file_name}"

        try:
            print(f"Starting transcription of: {file_name}")

            api_key = os.getenv("DEEPGRAM_API_KEY")
            if not api_key:
                raise ValueError("DEEPGRAM_API_KEY not found in environment variables")

            deepgram = DeepgramClient(api_key)
            print("Deepgram client created successfully")

            options = PrerecordedOptions(
                model="nova-3",
                language="en",
                smart_format=True,
                punctuate=True,
                paragraphs=True,
                diarize=True,
                filler_words=False,
            )

            # Check if file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            # Read the local file and transcribe it
            print("Starting transcription...")
            with open(audio_file_path, "rb") as audio_file:
                response = deepgram.listen.rest.v("1").transcribe_file(
                    {"buffer": audio_file},
                    options,
                )

            # Save the response json to the deepgram_transcripts directory
            # The file name should be the audio file name without the extension
            base_file_name = audio_file_path.split("/")[-1].split(".")[0]
            output_path = f"src/gent_disagreement_processor/data/raw/deepgram/{base_file_name}.json"

            with open(output_path, "w") as f:
                f.write(response.to_json(indent=4))

            print("Transcription completed successfully!")
            return output_path  # Return the path to the saved transcript

        except Exception as e:
            print(f"Exception: {e}")
            traceback.print_exc()
            return None  # Return None instead of empty string on failure
