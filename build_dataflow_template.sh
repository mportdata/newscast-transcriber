#!/bin/bash

# Build the Flex Template
#cp requirements.txt src/

gcloud dataflow flex-template build "gs://parallel-transcriber-dataflow-bucket/parallel-transcriber-template.json" \
  --project parallel-audio-transcriber \
  --image-gcr-path gcr.io/parallel-audio-transcriber/dataflow-transcriber-image:latest \
  --sdk-language "PYTHON" \
  --flex-template-base-image "PYTHON3" \
  --metadata-file "metadata.json" \
  --py-path "./src" \
  --env "FLEX_TEMPLATE_PYTHON_PY_FILE=src/main.py" \
  --env "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt"