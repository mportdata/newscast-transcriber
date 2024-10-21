#!/bin/bash

gcloud dataflow flex-template run "your-job-name" \
  --project=parallel-audio-transcriber \
  --region=europe-west2 \
  --template-file-gcs-location=gs://parallel-transcriber-dataflow-bucket/parallel-transcriber-template.json \
  --parameters base-path=gs://parallel-transcriber-dataflow-bucket/data \
  --parameters feed-url-file=gs://parallel-transcriber-dataflow-bucket/feeds.json
