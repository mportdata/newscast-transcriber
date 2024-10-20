import apache_beam as beam
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    GoogleCloudOptions,
    SetupOptions,
)
from apache_beam.options.pipeline_options import StandardOptions
import json
from modules.feed import Feed
from modules.models import Transcriber
from modules.episode import Episode


class CustomPipelineOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        # Add custom arguments specific to your pipeline, but NOT --runner
        parser.add_argument(
            "--local-base-path",
            default="./data",
            help="Local base path for saving output files when running locally",
        )
        parser.add_argument(
            "--gcs-base-path",
            default="gs://parallel-transcriber-dataflow-bucket/output",
            help="Google Cloud Storage base path for saving output files when running on Dataflow",
        )
        parser.add_argument(
            "--feed-url-json",
            default="""{
                "Fox News Hourly Update": "https://feeds.megaphone.fm/FOXM2252206613",
                "CNN Breaking News Alerts": "https://feeds.megaphone.fm/WMHY6108281879",
                "NPR News": "https://feeds.npr.org/500005/podcast.xml",
                "BBC Global News Podcast": "https://podcasts.files.bbci.co.uk/p02nq0gn.rss"
            }""",
            help="JSON string containing the feed URL dictionary",
        )


# Retrieve options from the command line or default
options = PipelineOptions()

# Parse custom options
custom_options = options.view_as(CustomPipelineOptions)

# Access runner through StandardOptions
standard_options = options.view_as(StandardOptions)

# Check if running locally or on Dataflow
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = "parallel-audio-transcriber"
google_cloud_options.region = "europe-west2"
google_cloud_options.job_name = "parallel-transcriber-dataflow-job"
google_cloud_options.staging_location = (
    "gs://parallel-transcriber-dataflow-bucket/staging"
)
google_cloud_options.temp_location = "gs://parallel-transcriber-dataflow-bucket/temp"

# Define template location only if you are creating a template
google_cloud_options.template_location = (
    "gs://parallel-transcriber-dataflow-bucket/templates/parallel_transcriber_template"
)

# Ensure the main session state is saved
options.view_as(SetupOptions).save_main_session = True

# Print the runner being used
print(f"Runner set: {standard_options.runner}")

# Determine the base path based on the runner
if standard_options.runner == "DataflowRunner":
    base_path = custom_options.gcs_base_path  # Cloud path for Dataflow
else:
    base_path = custom_options.local_base_path  # Local path for local execution

print(f"Base path set to: {base_path}")


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


def run_pipeline(pipeline_options):
    # Parse the feed URL JSON from the pipeline options
    feed_url_json = pipeline_options.view_as(CustomPipelineOptions).feed_url_json
    print(feed_url_json)

    # Convert the JSON string to a dictionary
    if feed_url_json:
        rss_feed_dictionary = json.loads(feed_url_json)
    else:
        raise ValueError("Feed URL JSON is not provided or empty.")
    # Formatting the channel names with commas and 'and' before the last one
    channel_names = list(rss_feed_dictionary.keys())
    formatted_channel_names = (
        ", ".join(channel_names[:-1]) + " and " + channel_names[-1]
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
            | "Get Latest Episode"
            >> beam.ParDo(
                GetLatestEpisode(
                    base_path=pipeline_options.view_as(
                        CustomPipelineOptions
                    ).gcs_base_path
                )
            )
            | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode(transcriber))
            | "Print Results" >> beam.Map(print)
        )

    print("Pipeline execution completed.")


if __name__ == "__main__":
    print("Starting Beam pipeline...")
    run_pipeline(custom_options)
    print("Beam pipeline finished.")
