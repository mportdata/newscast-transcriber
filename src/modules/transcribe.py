import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from modules.types import Episode


class Transcriber:
    def __init__(self):
        model_name = "openai/whisper-medium"
        self.processor = WhisperProcessor.from_pretrained(model_name)
        model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = model.to(self.device)


def transcribe_episode(
    transcriber: Transcriber, episode_title: str, chunk_size: int = 30
) -> str:
    filename = "".join([c if c.isalnum() else "_" for c in episode_title]) + ".mp3"
    audio, rate = librosa.load(f"podcasts/{filename}", sr=16000)

    total_duration = librosa.get_duration(y=audio, sr=rate)
    transcription = ""

    # Split audio into chunks and transcribe each chunk
    for start in range(0, int(total_duration), chunk_size):
        print(f"{round(100*start/int(total_duration),2)}% complete")
        end = min(start + chunk_size, int(total_duration))
        audio_chunk = audio[int(start * rate) : int(end * rate)]

        # Preprocess the chunk
        input_features = transcriber.processor(
            audio_chunk, sampling_rate=16000, return_tensors="pt"
        )
        input_features = input_features.to(transcriber.device)

        # Generate transcription for this chunk
        predicted_ids = transcriber.model.generate(input_features["input_features"])
        chunk_transcription = transcriber.processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )[0]

        transcription += chunk_transcription + " "  # Append the chunk transcription

    return transcription.strip()
