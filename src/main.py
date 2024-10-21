import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import json
from modules.feed import Feed
from modules.models import Transcriber
from modules.episode import Episode
from apache_beam.io.filesystems import FileSystems


class CustomPipelineOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--base-path",
            required=True,
            help="Base path for saving output files (local directory or GCS bucket)",
        )
        parser.add_argument(
            "--feed-url-file",
            required=True,
            help="Path to a JSON file containing the feed URL dictionary",
        )


class InitializeFeed(beam.DoFn):
    def process(self, feed_tuple):
        feed_name, feed_url = feed_tuple
        feed = Feed(feed_name, feed_url)
        yield feed


class GetLatestEpisode(beam.DoFn):
    def __init__(self, base_path):
        self.base_path = base_path

    def process(self, feed: Feed):
        episode = feed.get_latest_episode(base_path=self.base_path)
        yield episode


class TranscribeEpisode(beam.DoFn):
    def __init__(self, transcriber):
        self.transcriber = transcriber

    def process(self, episode: Episode):
        transcription = episode.transcribe_episode(self.transcriber)
        yield transcription


def run_pipeline(argv=None):
    # Parse pipeline options
    pipeline_options = PipelineOptions(argv)
    custom_options = pipeline_options.view_as(CustomPipelineOptions)

    base_path = custom_options.base_path
    print(f"Base path set to: {base_path}")

    # Read the feed URL JSON from the file
    feed_url_file = custom_options.feed_url_file
    if not feed_url_file:
        raise ValueError("Feed URL file is not provided.")

    with FileSystems.open(feed_url_file) as f:
        rss_feed_dictionary = json.load(f)

    # Formatting the channel names for display
    channel_names = list(rss_feed_dictionary.keys())
    formatted_channel_names = (
        ", ".join(channel_names[:-1]) + " and " + channel_names[-1]
        if len(channel_names) > 1
        else channel_names[0]
    )
    print(f"Fetching latest episodes from {formatted_channel_names}")

    # Initialize the transcriber
    transcriber = Transcriber("tiny")

    # Define the Beam pipeline
    with beam.Pipeline(options=pipeline_options) as pipeline:
        (
            pipeline
            | "Create PCollection of Feeds"
            >> beam.Create(list(rss_feed_dictionary.items()))
            | "Initialize Feed" >> beam.ParDo(InitializeFeed())
            | "Get Latest Episode" >> beam.ParDo(GetLatestEpisode(base_path=base_path))
            | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode(transcriber))
            | "Print Results" >> beam.Map(print)
        )

    print("Pipeline execution completed.")


if __name__ == "__main__":
    run_pipeline()
