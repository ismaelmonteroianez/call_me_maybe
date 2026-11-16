from src.models import FunctionDefinition
import json

def validate_start(generated: str) -> bool:
    expected = '{"name":"'
    return expected.startswith(generated)

def is_start_complete(generated: str) -> bool:
    return generated == '{"name":"'

def validate_function_name_prefix(
    functions: list[FunctionDefinition],
    generated: str) -> bool:
    for function in functions:
        if function.name.startswith(generated):
            return True
    return False

def validate_parameter_name_prefix(
    parameter_name: str,
    generated: str) -> bool:
        expected = json.dumps(parameter_name) + ":"
        return expected.startswith(generated)

def validate_string_prefix(generated: str) -> bool:
    if not generated.startswith('"'):
        return False
    escaped = False
    for char in generated[1:]:
        if escaped:
            if char not in '"\\/bfnrtu':
                return False
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return generated.endswith('"')
        elif ord(char) < 32:
            return False
    return True

def is_string_complete(generated: str) -> bool:
    if not generated.endswith('"'):
        return False
    escaped = False
    for char in generated[1:-1]:
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return False
    return True

def validate_number_prefix(generated: str) -> bool:
    if generated.startswith("-"):
        generated = generated[1:]
    if not generated:
        return True
    for char in generated:
        if char not in "0123456789.":
            return False
    parts = generated.split(".")
    if len(parts) > 2:
        return False
    if len(parts[0]) == 0:
        return False
    if len(parts[0]) > 1 and parts[0].startswith("0"):
        return False
    return True

def is_number_complete(generated: str) -> bool:
    try:
        value = json.loads(generated)
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    except json.JSONDecodeError:
        return False

def validate_boolean_prefix(generated: str) -> bool:
    if "true".startswith(generated):
        return True
    if "false".startswith(generated):
        return True
    return False

def is_function_name_complete(
    functions: list[FunctionDefinition],
    generated: str) -> bool:
    for function in functions:
        if function.name == generated:
            return True
    return False

def validate_parameters_start(generated: str) -> bool:
    expected = ',"parameters":{'
    return expected.startswith(generated)

def is_parameters_start_complete(generated: str) -> bool:
    return generated == ',"parameters":{'

def is_parameter_name_complete(parameter_name: str,
    generated: str) -> bool:
        return generated == json.dumps(parameter_name) + ":"

def is_boolean_complete(generated: str) -> bool:
    return generated in ("true", "false")

def validate_parameters_end(generated: str, has_more_parameters: bool) -> bool:
        expected = "," if has_more_parameters else "}"
        return expected.startswith(generated)

def is_parameters_end_complete(generated: str, has_more_parameters: bool) -> bool:
    expected = "," if has_more_parameters else "}"
    return generated == expected

def validate_end(generated: str) -> bool:
    return "}".startswith(generated)

def is_end_complete(generated: str) -> bool:
    return generated == "}"
