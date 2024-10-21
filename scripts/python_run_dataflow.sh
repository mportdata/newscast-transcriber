#!/bin/bash

python src/main.py \
    --runner DataflowRunner \
    --project parallel-audio-transcriber \
    --region europe-west2 \
    --temp_location gs://parallel-transcriber-dataflow-bucket/temp \
    --staging_location gs://parallel-transcriber-dataflow-bucket/staging \
    --base-path gs://parallel-transcriber-dataflow-bucket/data \
    --feed-url-file gs://parallel-transcriber-dataflow-bucket/feeds.json