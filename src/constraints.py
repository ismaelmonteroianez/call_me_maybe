from src.models import FunctionDefinition

def validate_fixed_prefix(expected: str, generated: str) -> bool:
    return expected.startswith(generated)

def validate_function_name_prefix(
    functions: list[FunctionDefinition],
    generated: str) -> bool:
    for function in functions:
        if function.name.startswith(generated):
            return True
    return False

def validate_parameter_name_prefix(
    function: FunctionDefinition,
    generated: str
) -> bool:
    for parameter_name in function.parameters:
        if parameter_name.startswith(generated):
            return True
    return False

def validate_string_prefix(generated: str) -> bool:
    if not generated.startswith('"'):
        return False
    if generated.endswith('"') and len(generated) == 2:
        return False
    for char in generated[1:]:
        if ord(char) < 32:
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

def validate_boolean_prefix(generated: str) -> bool:
    if "true".startswith(generated):
        return True
    if "false".startswith(generated):
        return True
    return False
