import apache_beam as beam
import requests
from modules.ingest import get_episode_data_from_feed, download_episode


class DownloadEpisode(beam.DoFn):
    def process(self, element):
        episode_title, episode_info = element

        if episode_info:
            episode_url = episode_info["url"]
            download_episode(episode_title, episode_url)
        else:
            yield f"Episode data not found for {episode_title}"


def run_pipeline(podcast_feed_url):
    episode_data = get_episode_data_from_feed(podcast_feed_url)

    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "Create PCollection of Titles" >> beam.Create(list(episode_data.keys()))
            | "Pair Titles with Data"
            >> beam.Map(lambda title: (title, episode_data[title]))
            | "Download Episode" >> beam.ParDo(DownloadEpisode())
            | "Print Results" >> beam.Map(print)
        )


if __name__ == "__main__":
    FEED_URL = "https://feeds.libsyn.com/519643/rss"
    run_pipeline(FEED_URL)


# (
# pipeline
# | "Create Feed URL" >> beam.Create(list(episode_data.keys()))
# | "Download Episode" >> beam.ParDo(DownloadEpisode())
# | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode())
# | "Extract Fit Check Segment" >> beam.ParDo(ExtractFitCheckSegment())
# | "Generate JSON" >> beam.ParDo(GenerateJSON())
# | "Print Results" >> beam.Map(print)
# )
