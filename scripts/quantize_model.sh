#!/bin/bash

# Check if a model name was provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <model_name>"
  exit 1
fi

# Store the model name from the CLI argument
MODEL_NAME=$1

# Export the specified model to ONNX format
echo "Exporting $MODEL_NAME to ONNX format..."
optimum-cli export onnx --model "$MODEL_NAME" models/$MODEL_NAME/

# Quantize the ONNX model for ARM64 architecture
echo "Quantizing the ONNX model for ARM64 architecture..."
optimum-cli onnxruntime quantize --onnx_model models/$MODEL_NAME/ --arm64 -o models/${MODEL_NAME}_quantized/

echo "Model $MODEL_NAME has been successfully exported and quantized."
