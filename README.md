*This project has been created as part of the 42 curriculum by ismonter.*

# Call Me Maybe

> Introduction to function calling in LLMs

## Description

Call Me Maybe is a Python project that explores function calling with Large Language Models (LLMs).

The program receives a list of user prompts and a list of available function definitions. For each prompt, the language model selects the most appropriate function and extracts the arguments required to call it.

The project uses the Qwen3-0.6B model through the provided `llm_sdk` package.

The main objective is to generate structured JSON function calls while ensuring that the output follows the expected format and respects the available function definitions.

To achieve this, the project implements constrained decoding using a state machine. This allows the program to validate the generated content during token generation rather than relying on post-processing to correct the final output.

The language model handles the semantic task of understanding the user's request, selecting a function and extracting its arguments. The state machine enforces the structural constraints of the generated JSON.

## Instructions

### Requirements

- Python 3.10 or higher
- `uv`
- CPU-compatible environment

### Installation

Clone the repository and navigate to the project directory.

Install the dependencies using:

    make install

This command runs `uv sync`, which installs the project dependencies and prepares the environment.

### Execution

Run the project using:

    make run

By default, the program reads the following files:

- `data/input/function_calling_tests.json`: contains the user prompts.
- `data/input/functions_definition.json`: contains the available function definitions.

The generated results are saved to:

- `data/output/function_calling_results.json`

Custom input, function definition and output paths can also be provided:

    uv run python -m src --input <input_file> --functions_definition <functions_file> --output <output_file>

### Other commands

- `make debug`: runs the program using Python's debugger.
- `make lint`: runs Flake8 and Mypy.
- `make clean`: removes Python cache files and temporary build directories.
- `make fclean`: performs `clean` and removes the project virtual environment.

## Project structure

The project is organized into the following directories and files:

- `src/`
  - `__main__.py`: handles the main execution loop, model inference, constrained decoding and result generation.
  - `parser.py`: loads and validates the input JSON files.
  - `models.py`: defines the Pydantic models used to validate prompts and function definitions.
  - `instructions.py`: builds the prompts sent to the language model.
  - `llm_handler.py`: provides an interface to the language model through `llm_sdk`.
  - `state_machine.py`: manages the states and transitions during constrained decoding.
  - `constraints.py`: contains the validation rules for the generated JSON content.
- `data/`
  - `input/`: contains the input prompts and function definitions.
  - `output/`: stores the generated function calls.
- `llm_sdk/`: contains the provided language model SDK.
- `Makefile`: defines the project commands.
- `pyproject.toml`: defines project metadata and dependencies.
- `uv.lock`: records the resolved dependency versions.

## Resources

The following resources were useful during the development of this project:

- [Python documentation](https://docs.python.org/3/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [NumPy documentation](https://numpy.org/doc/)
- [Hugging Face documentation](https://huggingface.co/docs)
- [Qwen documentation](https://qwen.readthedocs.io/)
- [JSON specification](https://www.json.org/json-en.html)

### AI usage

Artificial Intelligence tools, including ChatGPT, were used as development support throughout the project.

They were used for:
- Understanding concepts related to Large Language Models, function calling and constrained decoding.
- Discussing possible implementation approaches and evaluating technical decisions.
- Debugging and understanding Python code, particularly the state machine and JSON validation logic.
- Reviewing code and identifying potential improvements.
- Preparing explanations and documentation for the project.
AI was used as an assistance tool. The implementation decisions, code integration, testing and verification of the final solution were carried out by the project author.

## Algorithm explanation

The project combines a language model with a state machine to generate structured function calls.

The process is divided into several stages.

### 1. Input parsing

The program loads the input prompts and function definitions from JSON files.

Pydantic models validate the input structure, checking that the required fields exist and that their values have the expected types.

The validation also checks that:

- Prompts are not empty.
- Function names and descriptions are not empty.
- Parameter names are valid and not duplicated.
- Function names are not duplicated.
- Parameter and return types belong to the supported types.

The supported parameter and return types are:

- `string`
- `number`
- `integer`
- `boolean`

### 2. Prompt construction

For each user request, the program builds a prompt containing:

- Instructions for the language model.
- The available function definitions.
- The user's request.
- The expected JSON response format.

The model is instructed to select one of the available functions and extract its arguments without executing it.

The expected response is a JSON object containing the function name and its parameters.

### 3. Model inference

The prompt is encoded into token IDs and passed to the language model.

The model returns logits representing the scores of the possible next tokens.

The program selects the token with the highest logit using `numpy.argmax`.

The selected token ID is decoded into text so that it can be checked by the state machine.

### 4. Constrained decoding

A state machine controls the structure of the generated JSON.

It tracks the current generation state and validates each candidate token before accepting it.

The state machine includes the following states:

- `START`: expects the beginning of the JSON object and the function name field.
- `NAME`: generates and validates the selected function name.
- `PARAMETERS_START`: expects the beginning of the parameters object.
- `PARAMETER_NAME`: generates and validates the name of the next expected parameter.
- `PARAMETER_VALUE`: generates and validates the parameter value according to its declared type.
- `PARAMETERS_END`: handles the end of the parameters object.
- `END`: marks the completion of the JSON structure.

The state machine checks the expected JSON structure, function names, parameter names, parameter values and their types.

String values are checked according to JSON string rules, while numeric and boolean values follow their respective validation rules.

The state machine also handles incomplete JSON fragments. A fragment that is not yet a complete JSON value can still be accepted if it is a valid prefix that can be completed by subsequent tokens.

### 5. Candidate validation

For each generation step, the program obtains the model's logits and selects the candidate with the highest score.

A deep copy of the current state machine is used to validate the candidate before modifying the actual generation state. This prevents rejected candidates from changing the state of the ongoing generation.

If the candidate is valid, the copied state machine becomes the current state and the token is added to the generated text.

If the candidate is invalid, its logit is assigned negative infinity (`-inf`). The program then selects the next highest-scoring candidate and validates it again.

This process avoids decoding and validating every vocabulary token in advance. The logits array is still examined when selecting the highest-scoring candidate.

### 6. Result generation

The generation process continues until the generated text can be parsed as a complete JSON object.

Once a valid JSON object has been obtained, the original user prompt is added to the result.

The results for all prompts are collected and saved to the output JSON file.

The program generates function call descriptions. It does not execute the selected functions.

## Design decisions

### Constrained decoding instead of post-processing

Rather than allowing the model to generate unrestricted text and correcting the result afterwards, the project validates candidate tokens during generation.

This approach prevents invalid structural elements from being accepted in the first place and guides the model towards the expected JSON format.

### State machine

A state machine was chosen because JSON generation follows a sequence of well-defined structural stages.

Each state has specific validation rules, making the generation process easier to control and understand.

It also separates the validation logic for function names, parameter names and parameter values.

### Separating structural validation from semantic selection

The language model is responsible for understanding the user's request, selecting the appropriate function and extracting its arguments.

The state machine is responsible for enforcing structural constraints, including function names, parameter names, value types and JSON syntax.

This separation is important because structural validity does not necessarily imply semantic correctness. The generated function call can follow the expected schema while still containing an incorrect function selection or incorrectly extracted arguments.

### Using a copy of the state machine

A deep copy of the state machine is used to test each candidate token before applying its changes to the actual generation state.

This prevents rejected candidates from modifying the current state and allows the program to safely try alternative tokens.

### Pydantic for input validation

Pydantic models provide a clear way to validate the input files and ensure that function definitions and prompts follow the expected structure.

This also makes the supported data types explicit.

### CPU compatibility

The project uses the provided `llm_sdk` interface and does not directly implement GPU-specific operations.

This is important because the project must run on the hardware available at 42 schools, where CPU execution and limited memory are relevant constraints.

## Performance analysis

The project was tested on the CPU-based hardware available at 42.

Generating the complete output for the 11 supplied prompts took approximately 230 seconds.

The subject requires the execution to complete in less than 5 minutes, so this execution remained within the required time limit.

The implementation selects the highest-scoring token using `numpy.argmax`. If that token is rejected by the state machine, its score is set to negative infinity and the next candidate is evaluated.

Although finding the maximum logit requires examining the logits array, this approach avoids decoding and validating every vocabulary token in advance.

Execution time depends on the hardware, system load, prompt length and number of generated tokens. Therefore, the measured execution time may vary between machines.

### Accuracy and reliability

The 11 supplied test prompts produced the expected function names and extracted parameters in our tests.

Constrained decoding ensures that the generated output follows the structural rules implemented by the state machine, including the expected function names, parameter names, value types and JSON format.

However, structural validity does not guarantee semantic accuracy. The language model is still responsible for selecting the appropriate function and extracting the correct arguments. Therefore, an incorrect semantic interpretation can still produce a structurally valid function call.

This distinction is important when evaluating the reliability of the solution.

## Challenges faced

### Understanding constrained decoding

One of the main challenges was understanding how to restrict the language model's output without replacing its ability to interpret user requests.

The solution was to separate semantic decisions, handled by the language model, from structural validation, handled by the state machine.

### Managing generation states

Implementing the state machine required handling different types of JSON values and their respective generation rules.

Strings, integers, numbers and booleans require different validation logic, especially when a value is generated across multiple tokens.

### Validating incomplete JSON

During generation, the output is often an incomplete JSON fragment.

The validation logic therefore needs to distinguish between an invalid fragment and a valid prefix that can become a complete JSON value with additional tokens.

This was particularly relevant for strings and numeric values, whose final validity may only be determined once the value is complete.

### Handling rejected tokens

A candidate token can have the highest model score but still be incompatible with the current state of the JSON structure.

The program therefore needs to reject that candidate without corrupting the generation state and continue with the next highest-scoring token.

Using a deep copy of the state machine makes this possible.

### Performance limitations

Running a language model on CPU-only hardware presented a performance challenge.

The generation process had to remain within the execution time required by the subject while operating with the available hardware resources.

## Testing strategy

The project was tested using the supplied input files, which contain 11 different user requests.

These examples cover:

- Addition of numbers.
- Greeting a person.
- Reversing strings.
- Calculating square roots.
- Replacing numbers using regular expressions.
- Replacing vowels in strings.
- Substituting words in strings.

The generated function names and parameters were checked against the expected function definitions.

The supplied examples produced the expected function names and extracted parameters.

Additional manual tests were performed using different prompts, including requests that did not clearly correspond to an available function.

These tests helped verify the distinction between structural validity and semantic correctness: constrained decoding can ensure that the generated output follows the structural constraints implemented by the state machine, but it cannot guarantee that the selected function or extracted arguments are meaningful for every possible request.

Static analysis can be performed using:

    make lint

This runs Flake8 and Mypy with the project's configured checks.

## Example usage

The following example shows how the program handles a request to add two numbers.

### Input prompt

    What is the sum of 2 and 3?

### Available function

    {
        "name": "fn_add_numbers",
        "description": "Add two numbers",
        "parameters": {
            "a": {
                "type": "number"
            },
            "b": {
                "type": "number"
            }
        },
        "returns": {
            "type": "number"
        }
    }

### Expected output

    {
        "prompt": "What is the sum of 2 and 3?",
        "name": "fn_add_numbers",
        "parameters": {
            "a": 2,
            "b": 3
        }
    }
The program generates a function call description in JSON format. It does not execute the selected function.