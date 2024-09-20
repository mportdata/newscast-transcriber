import apache_beam as beam
from modules.feed import Feed
from modules.episode import Episode
from modules.models import Transcriber, FitCheckExtractor


class DownloadEpisode(beam.DoFn):
    def process(self, episode):
        episode_title = (
            episode.title
        )  # Access the title directly from the episode object
        if episode:
            print(f"Downloading episode: {episode_title}")

            # Ensure download is invoked
            episode.download_episode()
            print(f"Finished downloading episode: {episode_title}")

            # Yield the episode object back to the pipeline for transcription
            yield episode
        else:
            print(f"Episode data not found for {episode_title}")
            yield f"Episode data not found for {episode_title}"


class TranscribeEpisode(beam.DoFn):
    def __init__(self, transcriber):
        self.transcriber = transcriber

    def process(self, episode):
        episode_title = (
            episode.title
        )  # Access the title directly from the episode object

        if episode:
            print(f"Transcribing episode: {episode_title}")
            transcription = episode.transcribe_episode(self.transcriber)
            print(f"Finished transcribing episode: {episode_title}")
            yield (episode_title, transcription)  # Return the transcription result
        else:
            print(f"Skipping transcription for {episode_title}, no episode data.")
            yield (episode_title, "No episode data available for transcription.")


class ExtractFitCheck(beam.DoFn):
    def __init__(self, fit_check_extractor):
        self.fit_check_extractor = fit_check_extractor

    def process(self, episode):
        episode_title = (
            episode.title
        )  # Access the title directly from the episode object
        yield (episode_title, "Test of Extact fit check step ran")


def run_pipeline(podcast_feed_url, episode_limit=0):
    # Initialize feed and transcriber
    print(f"Fetching episodes from feed URL: {podcast_feed_url}")
    feed = Feed(podcast_feed_url)
    episode_data = feed.get_interview_episodes(episode_limit=episode_limit)
    print(f"Number of episodes fetched: {len(episode_data)}")

    transcriber = Transcriber("tiny")
    fit_check_extractor = FitCheckExtractor()

    # Define the Beam pipeline
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "Create PCollection of Episodes"
            >> beam.Create(list(episode_data.values()))  # Use episode objects directly
            | "Download Episode" >> beam.ParDo(DownloadEpisode())
            | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode(transcriber))
            | "Extract Fit Check" >> beam.ParDo(ExtractFitCheck(fit_check_extractor))
            | "Print Results" >> beam.Map(print)
        )

    print("Pipeline execution completed.")


if __name__ == "__main__":
    FEED_URL = "https://feeds.libsyn.com/519643/rss"
    print("Starting Beam pipeline...")
    run_pipeline(FEED_URL, 1)
    print("Beam pipeline finished.")
