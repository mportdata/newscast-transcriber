import os
import requests
from pathlib import Path
from modules.models import Transcriber, FitCheckExtractor
import librosa
import math


class Episode:
    def __init__(self, title, url, release_date):
        self.title = title
        self.url = url
        self.release_date = release_date
        self.filename = "".join([c if c.isalnum() else "_" for c in title])

    def downloaded_status(self):
        file_path = Path(f"podcasts/{self.filename}.mp3")
        return file_path.exists()

    def transcribed_status(self):
        file_path = Path(f"transcriptions/{self.filename}.txt")
        return file_path.exists()

    def download_episode(self):
        if self.downloaded_status():
            print(f"Already Downloaded: {self.title}")
            return {"status": "success", "message": "Episode already downloaded"}

        save_dir = "podcasts"
        os.makedirs(save_dir, exist_ok=True)

        filename_mp3 = self.filename + ".mp3"
        file_path = os.path.join(save_dir, filename_mp3)

        print(f"Downloading first quarter of: {self.title}")

        # Send the request and get headers to find out the content length
        response = requests.get(self.url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))
            episode_divider = 3
            quarter_size = total_size // episode_divider

            downloaded_size = 0  # Keep track of the downloaded size
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                    # Stop downloading once we have the first quarter
                    if downloaded_size >= quarter_size:
                        print(
                            f"Stopped downloading after first {100/episode_divider}% of {self.title}"
                        )
                        break

            print(f"Downloaded first quarter of: {self.title}")
            return {
                "status": "success",
                "message": "First quarter of episode downloaded successfully",
            }
        else:
            print(f"Failed to download: {self.title}")
            return {"status": "error", "message": "Failed to download episode"}

    def transcribe_episode(self, transcriber: Transcriber):
        if not self.downloaded_status():
            self.download_episode()
        if self.transcribed_status():
            print(f"Already Transcribed: {self.title}")
            return {"status": "success", "message": "Episode already transcribed"}

        save_dir = "transcriptions"
        os.makedirs(save_dir, exist_ok=True)

        chunk_size = 30
        sampling_rate = 16000
        audio_file_path = f"podcasts/{self.filename}.mp3"
        audio, rate = librosa.load(audio_file_path, sr=sampling_rate)
        total_duration = librosa.get_duration(y=audio, sr=sampling_rate)
        transcription = ""
        time_cap = math.ceil(total_duration)

        # Split audio into chunks and transcribe each chunk
        for start in range(0, time_cap, chunk_size):
            print(
                f"Transcription of {self.filename}: {round(100*start/int(time_cap),2)}% complete"
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
            f"{save_dir}/{self.filename}.txt"  # Specify the path and filename
        )

        # Save the transcription to a .txt file
        with open(transcription_file_path, "w") as file:
            file.write(transcription.strip())

        print(f"Transcription of {self.filename}: 100% complete")
        return transcription.strip()

    def extract_fit_check(self, fit_check_extractor: FitCheckExtractor):
        if not self.downloaded_status():
            self.download_episode()
        if not self.transcribed_status():
            self.transcribe_episode()

    def __eq__(self, other):
        if isinstance(other, Episode):
            return (
                self.title == other.title
                and self.url == other.url
                and self.release_date == other.release_date
            )
        return False
