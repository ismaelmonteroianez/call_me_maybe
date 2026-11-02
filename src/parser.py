from src.models import PromptInput, FunctionDefinition
import json


def load_json(file_path: str) -> object:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_prompts(file_path: str) -> list[PromptInput]:
    data = load_json(file_path)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array")
    prompts = []
    for item in data:
        prompt = PromptInput.model_validate(item)
        prompts.append(prompt)
    return prompts


def load_function_definitions(file_path: str,) -> list[FunctionDefinition]:
    data = load_json(file_path)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array")
    functions = []
    for item in data:
        function = FunctionDefinition.model_validate(item)
        functions.append(function)
    return functions


def parser():
    prompts = load_prompts("data/input/function_calling_tests.json")
    functions = load_function_definitions("data/input/functions_"
                                          "definition.json")
    return (prompts, functions)
