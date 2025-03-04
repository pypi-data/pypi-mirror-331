"""Model tuning functionality for the Gemini API."""

from collections.abc import Sequence
from typing import Any, Dict, List, Optional

from .config import GeminiClient
from .types import TuningExample


class ModelTuner:
    """Handler for model fine-tuning operations."""

    def __init__(self, client: GeminiClient) -> None:
        """Initialize the tuner.

        Args:
            client: The Gemini API client
        """
        self.client = client

    def tune(
        self,
        examples: Sequence[TuningExample],
        base_model: Optional[str] = None,
        display_name: Optional[str] = None,
        learning_rate: float = 0.001,
        batch_size: int = 4,
        epoch_count: int = 5,
    ) -> str:
        """Fine-tune a model with examples.

        Args:
            examples: Training examples for tuning
            base_model: Optional base model to tune (defaults to client's model)
            display_name: Optional display name for the tuned model
            learning_rate: Learning rate for tuning
            batch_size: Batch size for training
            epoch_count: Number of epochs to train

        Returns:
            The name/ID of the tuned model
        """
        tuning_examples: List[Dict[str, str]] = [
            {
                "input": ex.input_text,
                "output": ex.output_text,
            }
            for ex in examples
        ]

        tuning_config: Dict[str, Any] = {
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "epoch_count": epoch_count,
        }
        if display_name:
            tuning_config["display_name"] = display_name

        response = self.client.tunings.tune(
            base_model=base_model or self.client.model_type,
            examples=tuning_examples,
            config=tuning_config,
        )
        # Handle both string and object responses
        return str(response)


class ModelUtils:
    """Utility functions for model operations."""

    def __init__(self, client: GeminiClient) -> None:
        """Initialize utilities.

        Args:
            client: The Gemini API client
        """
        self.client = client

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens in the text
        """
        response = self.client.models.count_tokens(text)
        if not hasattr(response, "total_tokens") or response.total_tokens is None:
            raise ValueError("Model returned no token count")
        return response.total_tokens

    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text.

        Args:
            text: Text to generate embeddings for

        Returns:
            List of embedding values
        """
        response = self.client.models.embed_content(
            text,
            model="embedding-001",  # Use dedicated embedding model
        )
        if not hasattr(response, "embeddings") or not response.embeddings:
            raise ValueError("Model returned empty embeddings")
        return list(response.embeddings[0])
