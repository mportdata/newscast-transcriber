import os
import requests


class Episode:
    def __init__(self, title, url, release_date):
        self.title = title
        self.url = url
        self.release_date = release_date
        self.filename = "".join([c if c.isalnum() else "_" for c in title])

    def downloaded_status(self):
        return True

    def transcribed_status(self):
        return True

    def download_episode(self, save_dir="podcasts"):
        os.makedirs(save_dir, exist_ok=True)

        filename_mp3 = self.filename + ".mp3"
        file_path = os.path.join(save_dir, filename_mp3)

        print(f"Downloading: {self.title}")

        # Download the episode using requests
        response = requests.get(self.url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded: {self.title}")
        else:
            print(f"Failed to download: {self.title}")

    def __eq__(self, other):
        if isinstance(other, Episode):
            return (
                self.title == other.title
                and self.url == other.url
                and self.release_date == other.release_date
            )
        return False
