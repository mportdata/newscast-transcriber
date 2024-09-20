import torch
import librosa
from transformers import (
    pipeline,
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoModelForCausalLM,
    AutoTokenizer,
)
import bitsandbytes as bnb


class Transcriber:
    def __init__(self, model_size="tiny"):
        model_name = f"openai/whisper-{model_size}"

        # Logging the model name being loaded
        print(f"Loading Whisper model: {model_name}")

        try:
            # Load the Whisper processor
            self.processor = WhisperProcessor.from_pretrained(model_name)
            print(f"Processor loaded successfully for model: {model_name}")
        except Exception as e:
            print(f"Error loading processor for model {model_name}: {e}")
            raise

        try:
            # Load the Whisper model
            print(f"Loading the Whisper model for conditional generation...")
            model = WhisperForConditionalGeneration.from_pretrained(model_name)
            print(f"Model loaded successfully for model: {model_name}")
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            raise

        # Check if CUDA is available and assign the appropriate device
        try:
            self.device = "cpu"
            print(f"Using device: {self.device}")
        except Exception as e:
            print(f"Error determining device: {e}")
            raise

        try:
            # Move the model to the correct device (CPU/GPU)
            self.model = model.to(self.device)
            print(f"Model successfully moved to device: {self.device}")
        except Exception as e:
            print(f"Error moving model to device {self.device}: {e}")
            raise


class FitCheckExtractor:
    def __init__(self, model_name="distilgpt2"):
        # Always use CPU since no GPU is available
        self.device = "cpu"
        print(f"Using device: {self.device}")

        try:
            # Load the tokenizer
            print(f"Loading tokenizer for {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Load model without quantization, for CPU
            print("Loading model in full precision (FP32)...")
            self.model = AutoModelForCausalLM.from_pretrained(model_name).to(
                self.device
            )

            print(f"Model loaded and moved to {self.device} successfully.")
        except Exception as e:
            print(f"Error loading model or tokenizer: {e}")
            raise
