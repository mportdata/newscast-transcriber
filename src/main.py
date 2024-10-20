import apache_beam as beam
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    GoogleCloudOptions,
    SetupOptions,
    StandardOptions,
)
import json
from modules.feed import Feed
from modules.models import Transcriber
from modules.episode import Episode


class CustomPipelineOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--local-base-path",
            default="./data",
            help="Local base path for saving output files when running locally",
        )
        parser.add_argument(
            "--gcs-base-path",
            help="Google Cloud Storage base path for saving output files when running on Dataflow",
        )
        parser.add_argument(
            "--feed-url-json",
            help="JSON string containing the feed URL dictionary",
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
    # Use argument parsing to extract runtime options
    pipeline_options = PipelineOptions(argv)

    # Parse custom options
    custom_options = pipeline_options.view_as(CustomPipelineOptions)
    google_cloud_options = pipeline_options.view_as(GoogleCloudOptions)
    standard_options = pipeline_options.view_as(StandardOptions)

    # Determine the base path based on the runner
    base_path = (
        custom_options.gcs_base_path
        if standard_options.runner == "DataflowRunner"
        else custom_options.local_base_path
    )
    print(f"Base path set to: {base_path}")

    # Parse the feed URL JSON from the pipeline options
    feed_url_json = custom_options.feed_url_json
    if not feed_url_json:
        raise ValueError("Feed URL JSON is not provided or empty.")
    rss_feed_dictionary = json.loads(feed_url_json)

    # Formatting the channel names with commas and 'and' before the last one
    channel_names = list(rss_feed_dictionary.keys())
    formatted_channel_names = (
        ", ".join(channel_names[:-1]) + " and " + channel_names[-1]
        if len(channel_names) > 1
        else channel_names[0]
    )
    print(f"Fetching latest episodes from {formatted_channel_names}")

    # Initialize the transcriber
    transcriber = Transcriber("tiny")

    # Define the Beam pipeline using the custom options
    with beam.Pipeline(options=pipeline_options) as pipeline:
        (
            pipeline
            | "Create PCollection of Feeds"
            >> beam.Create(
                list(rss_feed_dictionary.items())
            )  # Pass key-value pairs as (name, url)
            | "Initialize Feed" >> beam.ParDo(InitializeFeed())
            | "Get Latest Episode" >> beam.ParDo(GetLatestEpisode(base_path=base_path))
            | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode(transcriber))
            | "Print Results" >> beam.Map(print)
        )

    print("Pipeline execution completed.")


if __name__ == "__main__":
    run_pipeline()
