from llm_sdk import Small_LLM_Model
import json

class LLMHandler:

    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        self.model = Small_LLM_Model(self.model_name)

    def encode_prompt(self, prompt: str) -> list[int]:
        encoded = self.model.encode(prompt)
        return encoded[0].tolist()

    def get_logits(self, input_ids: list[int]) -> list[float]:
        return self.model.get_logits_from_input_ids(input_ids)

    def get_vocab_path(self) -> str:
        return self.model.get_path_to_vocab_file()

    def decode_prompt(self, prompt: str):
        decode = self.model.decode(prompt)
        return decode

    def load_vocabulary(self):
        tokenizer_path = self.model.get_path_to_tokenizer_file()
        with open(tokenizer_path, "r", encoding="utf-8") as file:
            tokenizer_data = json.load(file)
        token_to_id = tokenizer_data["model"]["vocab"]
        for token in tokenizer_data["added_tokens"]:
            token_to_id[token["content"]] = token["id"]
        return token_to_id

    def get_best_token(self, logits: list[float]) -> int:
        next_id = 0
        for token_id, logit in enumerate(logits):
            if logit > logits[next_id]:
                next_id = token_id
        return next_id
