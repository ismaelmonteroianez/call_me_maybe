from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
import json
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

    def get_vocab_path(self) -> str:
        """Return the path to the model's vocabulary file."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return cast(str, self.model.get_path_to_vocab_file())

    def decode_prompt(self, prompt: list[int]) -> str:
        """Decode a list of token IDs into text."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return cast(str, self.model.decode(prompt))

    def load_vocabulary(self) -> dict[str, int]:
        """Load the tokenizer vocabulary, including added tokens."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        tokenizer_path = self.model.get_path_to_tokenizer_file()
        with open(tokenizer_path, "r", encoding="utf-8") as file:
            tokenizer_data = json.load(file)
        token_to_id = tokenizer_data["model"]["vocab"]
        for token in tokenizer_data["added_tokens"]:
            token_to_id[token["content"]] = token["id"]
        return cast(dict[str, int], token_to_id)

    def get_best_token(self, logits: list[float]) -> int:
        """Return the token ID with the highest logit."""
        next_id = 0
        for token_id, logit in enumerate(logits):
            if logit > logits[next_id]:
                next_id = token_id
        return next_id
