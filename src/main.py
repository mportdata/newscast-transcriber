import apache_beam as beam
from modules.feed import Feed
from modules.models import Transcriber
from modules.episode import Episode


class InitializeFeed(beam.DoFn):
    def process(self, feed_tuple):
        feed_name, feed_url = feed_tuple
        feed = Feed(feed_name, feed_url)
        yield feed


class GetLatestEpisode(beam.DoFn):
    def process(self, feed: Feed):
        episode = feed.get_latest_episode()
        yield episode


class TranscribeEpisode(beam.DoFn):
    def __init__(self, transcriber):
        self.transcriber = transcriber

    def process(self, episode: Episode):
        transcription = episode.transcribe_episode(self.transcriber)
        yield transcription


def run_pipeline(rss_feed_dictionary):
    # Formatting the channel names with commas and 'and' before the last one
    channel_names = list(rss_feed_dictionary.keys())
    formatted_channel_names = (
        ", ".join(channel_names[:-1]) + " and " + channel_names[-1]
    )

    print(f"Fetching latest episodes from {formatted_channel_names}")

    # Initialize the transcriber
    transcriber = Transcriber("tiny")

    # Define the Beam pipeline
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "Create PCollection of Feeds"
            >> beam.Create(
                list(rss_feed_dictionary.items())
            )  # Pass key-value pairs as (name, url)
            | "Initialize Feed" >> beam.ParDo(InitializeFeed())
            | "Download Episode" >> beam.ParDo(GetLatestEpisode())
            | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode(transcriber))
            | "Print Results" >> beam.Map(print)
        )

    print("Pipeline execution completed.")


if __name__ == "__main__":
    feed_url_dict = {
        "Fox News Hourly Update": "https://feeds.megaphone.fm/FOXM2252206613",
        "CNN Breaking News Alerts": "https://feeds.megaphone.fm/WMHY6108281879",
        "NPR News": "https://feeds.npr.org/500005/podcast.xml",
        "BBC Global News Podcast": "https://podcasts.files.bbci.co.uk/p02nq0gn.rss",
    }
    print("Starting Beam pipeline...")
    run_pipeline(feed_url_dict)
    print("Beam pipeline finished.")
