import torch
import librosa
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoModelForCausalLM,
    AutoTokenizer,
)
from llama_cpp import Llama


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
    def __init__(self, model_name="Qwen/Qwen2-0.5B-Instruct-GGUF"):
        # Always use CPU since no GPU is available
        self.device = "cpu"
        print(f"Using device: {self.device}")

        try:
            llm = Llama.from_pretrained(
                repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
                filename="*q8_0.gguf",
                verbose=False,
            )

            output = llm(
                "Q: Name each planet in the solar system? A: ",  # Prompt
                max_tokens=32,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
                stop=[
                    "Q:",
                    "\n",
                ],  # Stop generating just before the model would generate a new question
                echo=True,  # Echo the prompt back in the output
            )  # Generate a completion, can also call create_completion
            print(output)
        except Exception as e:
            print(f"Error loading model or tokenizer: {e}")
            raise
