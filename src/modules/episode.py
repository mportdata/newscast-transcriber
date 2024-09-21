import os
import requests
from pathlib import Path
from modules.models import Transcriber
import librosa
import math
from datetime import datetime


class Episode:
    def __init__(
        self, channel_name: str, episode_name: str, url: str, release_datetime: datetime
    ):
        self.channel_name = channel_name
        self.episode_name = episode_name
        self.full_name = f"{channel_name}: {episode_name} ({release_datetime})"
        self.url = url
        self.release_datetime = release_datetime
        self.safe_channel_name = "".join(
            [c if c.isalnum() else "_" for c in channel_name]
        )
        self.safe_episode_name = f"{release_datetime}-{''.join([c if c.isalnum() else '_' for c in episode_name])}"

    def downloaded_status(self):
        file_path = Path(
            f"podcasts/{self.safe_channel_name}/{self.safe_episode_name}.mp3"
        )
        return file_path.exists()

    def transcribed_status(self):
        file_path = Path(
            f"transcriptions/{self.safe_channel_name}/{self.safe_episode_name}.txt"
        )
        return file_path.exists()

    def download_episode(self):
        if self.downloaded_status():
            print(f"Already Downloaded: {self.full_name}")
            return {"status": "success", "message": "Episode already downloaded"}

        save_dir = f"podcasts/{self.safe_channel_name}"
        os.makedirs(save_dir, exist_ok=True)

        filepath_mp3 = self.safe_episode_name + ".mp3"
        file_path = os.path.join(save_dir, filepath_mp3)

        print(f"Downloading: {self.full_name}")

        response = requests.get(self.url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

            print(f"Downloaded: {self.full_name}")
            return {
                "status": "success",
                "message": "Episode downloaded successfully",
            }
        else:
            print(f"Failed to download: {self.full_name}")
            return {"status": "error", "message": "Failed to download episode"}

    def transcribe_episode(self, transcriber: Transcriber):
        if not self.downloaded_status():
            self.download_episode()
        if self.transcribed_status():
            print(f"Already Transcribed: {self.full_name}")
            return {"status": "success", "message": "Episode already transcribed"}

        save_dir = f"transcriptions/{self.safe_channel_name}"
        os.makedirs(save_dir, exist_ok=True)

        chunk_size = 30
        sampling_rate = 16000
        audio_file_path = (
            f"podcasts/{self.safe_channel_name}/{self.safe_episode_name}.mp3"
        )
        audio, rate = librosa.load(audio_file_path, sr=sampling_rate)
        total_duration = librosa.get_duration(y=audio, sr=sampling_rate)
        transcription = ""
        time_cap = math.ceil(total_duration)

        # Split audio into chunks and transcribe each chunk
        for start in range(0, time_cap, chunk_size):
            print(
                f"Transcription of {self.full_name}: {round(100*start/int(time_cap),2)}% complete"
            )
            end = min(start + chunk_size, time_cap)
            audio_chunk = audio[start * rate : end * rate]

            # Preprocess the chunk
            input_features = transcriber.processor(
                audio_chunk, sampling_rate=sampling_rate, return_tensors="pt"
            )
            input_features = input_features.to(transcriber.device)

            # Generate transcription for this chunk
            predicted_ids = transcriber.model.generate(input_features["input_features"])
            chunk_transcription = transcriber.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )[0]

            transcription += chunk_transcription + " "  # Append the chunk transcription

        transcription_file_path = (
            f"{save_dir}/{self.safe_episode_name}.txt"  # Specify the path and filename
        )

        # Save the transcription to a .txt file
        with open(transcription_file_path, "w") as file:
            file.write(transcription.strip())

        print(f"Transcription of {self.full_name}: 100% complete")
        return transcription.strip()

    def get_transcription_text(self, transcriber: Transcriber):
        if not self.transcribed_status():
            self.transcribe_episode(transcriber)
        transcription_file_path = (
            f"transcriptions/{self.safe_channel_name}/{self.safe_episode_name}.txt"
        )
        try:
            # Open and read the transcription file
            with open(transcription_file_path, "r", encoding="utf-8") as file:
                print(f"Opening transcription file: {transcription_file_path}")
                text = file.read()
                print("File read successfully.")
                return text
        except Exception as e:
            print(f"Error reading file {transcription_file_path}: {e}")
            return None
