import apache_beam as beam
import requests


class DownloadEpisode(beam.DoFn):
    def process(self, element):
        # Download the audio file
        response = requests.get(element, stream=True)
        file_name = "episode.mp3"
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        yield file_name


def run_pipeline(podcast_feed_url):
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "Create Feed URL" >> beam.Create([podcast_feed_url])
            | "Download Episode" >> beam.ParDo(DownloadEpisode())
            # | "Transcribe Episode" >> beam.ParDo(TranscribeEpisode())
            # | "Extract Fit Check Segment" >> beam.ParDo(ExtractFitCheckSegment())
            # | "Generate JSON" >> beam.ParDo(GenerateJSON())
            # | "Print Results" >> beam.Map(print)
        )


if __name__ == "__main__":
    podcast_feed_url = "https://feeds.libsyn.com/519643/rss"
    run_pipeline(podcast_feed_url)
