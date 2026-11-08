from src.models import PromptInput, FunctionDefinition
import json


def load_json(file_path: str) -> object:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_prompts(file_path: str) -> list[PromptInput]:
    data = load_json(file_path)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array")
    if len(data) == 0:
        raise ValueError("No prompts found in input file")
    prompts = []
    for item in data:
        prompt = PromptInput.model_validate(item)
        prompts.append(prompt)
    return prompts


def load_function_definitions(file_path: str) -> list[FunctionDefinition]:
    data = load_json(file_path)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array")
    if len(data) == 0:
        raise ValueError("No function definitions found in input file")
    functions = []
    for item in data:
        function = FunctionDefinition.model_validate(item)
        functions.append(function)
    function_names = set()
    for function in functions:
        if function.name in function_names:
            raise ValueError(
                f"Duplicate function name: {function.name}")
        function_names.add(function.name)
    return functions


def parser(input_path: str,
    functions_definition_path: str) -> tuple[list[PromptInput], list[FunctionDefinition]]:
    prompts = load_prompts(input_path)
    functions = load_function_definitions(functions_definition_path)
    return (prompts, functions)
