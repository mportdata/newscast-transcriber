from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
)
import torch


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
            print("Loading the Whisper model for conditional generation...")
            model = WhisperForConditionalGeneration.from_pretrained(model_name)
            print(f"Model loaded successfully for model: {model_name}")
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            raise

        # Check if CUDA is available and assign the appropriate device
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
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
