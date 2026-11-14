import json

def build_prompt(functions, user_prompt: str) -> str:
    instructions = (
        "Choose the most appropriate function for the user's request.\n"
        "Extract its arguments from the request. Do not execute it.\n"
        'Return only a JSON object with the keys "prompt", '
        '"name" and "parameters", in that order.\n'
        "Copy the user's request exactly into the 'prompt' field.\n"
        "Return compact JSON on a single line.\n"
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
