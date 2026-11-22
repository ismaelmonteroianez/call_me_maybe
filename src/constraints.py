from src.models import FunctionDefinition
import json


def validate_start(generated: str) -> bool:
    """Check whether the generated text matches the expected JSON prefix."""
    expected = '{"name":"'
    return expected.startswith(generated)


def is_start_complete(generated: str) -> bool:
    """Check whether the initial JSON prefix is complete."""
    return generated == '{"name":"'


def validate_function_name_prefix(
                functions: list[FunctionDefinition],
                generated: str
                ) -> bool:
    """Check whether the generated text
    is a prefix of an available function name."""
    for function in functions:
        if function.name.startswith(generated):
            return True
    return False


def validate_parameter_name_prefix(
                parameter_name: str,
                generated: str
                ) -> bool:
    """Check whether the generated text
    is a valid prefix of a parameter name."""
    expected = json.dumps(parameter_name) + ":"
    return expected.startswith(generated)


def validate_string_prefix(generated: str) -> bool:
    """Check whether the generated text is a valid JSON string prefix."""
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
    """Check whether the generated text forms a complete JSON string."""
    if len(generated) < 2 or not generated.endswith('"'):
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


def validate_integer_prefix(generated: str) -> bool:
    """Check whether the generated text is a valid integer prefix."""
    if generated.startswith("-"):
        generated = generated[1:]
    if not generated:
        return True
    for char in generated:
        if char not in "0123456789":
            return False
    if len(generated) > 1 and generated.startswith("0"):
        return False
    return True


def is_integer_complete(generated: str) -> bool:
    """Check whether the generated text forms a complete integer."""
    try:
        value = json.loads(generated)
        return isinstance(value, int) and not isinstance(value, bool)
    except json.JSONDecodeError:
        return False


def validate_number_prefix(generated: str) -> bool:
    """Check whether the generated text is a valid number prefix."""
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
    """Check whether the generated text forms a complete number."""
    try:
        value = json.loads(generated)
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    except json.JSONDecodeError:
        return False


def validate_boolean_prefix(generated: str) -> bool:
    """Check whether the generated text is a valid boolean prefix."""
    if "true".startswith(generated):
        return True
    if "false".startswith(generated):
        return True
    return False


def is_function_name_complete(
                functions: list[FunctionDefinition],
                generated: str
                ) -> bool:
    """Check whether the generated text matches an available function name."""
    for function in functions:
        if function.name == generated:
            return True
    return False


def validate_parameters_start(generated: str) -> bool:
    """Check whether the generated text matches
    the expected parameters section prefix."""
    expected = '","parameters":{'
    return expected.startswith(generated)


def is_parameters_start_complete(generated: str) -> bool:
    """Check whether the parameters section prefix is complete."""
    return generated == '","parameters":{'


def is_parameter_name_complete(parameter_name: str,
                               generated: str) -> bool:
    """Check whether the generated parameter name is complete."""
    return generated == json.dumps(parameter_name) + ":"


def is_boolean_complete(generated: str) -> bool:
    """Check whether the generated text is a complete boolean value"""
    return generated in ("true", "false")


def validate_parameters_end(generated: str, has_more_parameters: bool) -> bool:
    """Check whether the generated text is a valid parameters section ending"""
    expected = "," if has_more_parameters else "}"
    return expected.startswith(generated)


def is_parameters_end_complete(generated: str,
                               has_more_parameters: bool) -> bool:
    """Check whether the parameters section ending is complete."""
    expected = "," if has_more_parameters else "}"
    return generated == expected


def validate_end(generated: str) -> bool:
    """Check whether the generated text matches the expected JSON ending."""
    return "}".startswith(generated)
