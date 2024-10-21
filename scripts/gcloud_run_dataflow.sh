#!/bin/bash

gcloud dataflow flex-template run "parallel-transcriber-job" \
  --template-file-gcs-location="gs://parallel-transcriber-dataflow-bucket/parallel-transcriber-template.json" \
  --project="parallel-audio-transcriber" \
  --region="europe-west2" \
  --parameters=base_path=gs://parallel-transcriber-dataflow-bucket/output