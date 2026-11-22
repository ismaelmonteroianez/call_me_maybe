import json
from src.models import FunctionDefinition


def build_prompt(functions: list[FunctionDefinition], user_prompt: str) -> str:
    """Build the model prompt with the available
    function definitions and the user's request."""
    instructions = (
        "Choose one of the available functions for the user's request.\n"
        "Extract its arguments from the request. Do not execute it.\n"
        'Return only a JSON object with the keys "name" and '
        '"parameters", in that order.\n'
        "Write compact JSON on a single line, without spaces outside "
        "string values or leading or trailing whitespace.\n"
        "Do not add extra keys, explanations or Markdown.\n"
        "Use the exact function name and parameter names.\n"
        "Respect the declared parameter types.\n"
        "Escape special characters as required by JSON.\n"
    )

    functions_dict = []

    for function in functions:
        functions_dict.append(function.model_dump())

    functions_json = json.dumps(functions_dict)

    prompt = (
        f"{instructions}\n"
        f"Available functions:\n{functions_json}\n\n"
        f"User request:\n{user_prompt}\n\n"
        "Response:\n"
    )

    return prompt
