from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from typing import cast


class LLMHandler:
    """Handle model loading, tokenization and inference operations."""

    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        """Initialize the handler with the selected model name."""
        self.model_name = model_name
        self.model: Small_LLM_Model | None = None

    def load_model(self) -> None:
        """Load the language model if it has not been loaded yet."""
        if self.model is None:
            self.model = Small_LLM_Model(self.model_name)

    def encode_prompt(self, prompt: str) -> list[int]:
        """Encode a text prompt into a list of token IDs."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        encoded = self.model.encode(prompt)
        return cast(list[int], encoded[0].tolist())

    def get_logits(self, input_ids: list[int]) -> list[float]:
        """Get the model's logits for the next token."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return cast(
            list[float],
            self.model.get_logits_from_input_ids(input_ids)
                    )

    def decode_prompt(self, prompt: list[int]) -> str:
        """Decode a list of token IDs into text."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return cast(str, self.model.decode(prompt))
