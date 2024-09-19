import apache_beam as beam
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
from modules.ingest import get_episode_data_from_feed, download_episode
from modules.transcriber import transcribe_episode


class DownloadEpisode(beam.DoFn):
    def process(self, element):
        episode_title, episode_info = element

        if episode_info:
            episode_url = episode_info["url"]
            download_episode(episode_title, episode_url)
        else:
            yield f"Episode data not found for {episode_title}"


class TranscribeEpisode(beam.DoFn):
    def __init__(self, processor, model):
        self.processor = processor
        self.model = model

    def process(self, element):
        episode_title, episode_info = element  # Expecting (title, info) pair
        audio_file_path = f"./podcasts/{episode_title}.mp3"  # Assumed file path

        # Call the transcribe function with the processor and model
        transcription = transcribe_episode(self.processor, self.model, audio_file_path)

        yield (episode_title, transcription)  # Return the transcription result


def run_pipeline(podcast_feed_url):
    episode_data = get_episode_data_from_feed(podcast_feed_url, 1)

    # Load the Whisper model and processor once, outside the DoFn
    processor = WhisperProcessor.from_pretrained("openai/whisper-small.en")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small.en")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "Create PCollection of Titles" >> beam.Create(list(episode_data.keys()))
            | "Pair Titles with Data"
            >> beam.Map(lambda title: (title, episode_data[title]))
            | "Download Episode" >> beam.ParDo(DownloadEpisode())
            | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode(processor, model))
            | "Print Results" >> beam.Map(print)
        )


if __name__ == "__main__":
    FEED_URL = "https://feeds.libsyn.com/519643/rss"
    run_pipeline(FEED_URL)
