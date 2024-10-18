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
        # Determine the device: GPU if available, otherwise CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        # Load the Whisper processor
        self.processor = WhisperProcessor.from_pretrained(model_name)
        model = WhisperForConditionalGeneration.from_pretrained(model_name)
        # Move the model to the correct device (CPU/GPU)
        self.model = model.to(self.device)
        print(f"Model successfully moved to device: {self.device}")
