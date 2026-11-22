import json
import sys
import argparse
import copy
import os
import time
from pydantic import ValidationError
import numpy as np
from src.parser import parser
from src.instructions import build_prompt
from src.llm_handler import LLMHandler
from src.state_machine import StateMachine


class NoValidTokenError(Exception):
    """Raised when no valid token can be generated."""
    pass


def parse_arguments() -> argparse.Namespace:
    """Parse the command-line arguments for input,
    function definitions and output paths."""
    argument_parser = argparse.ArgumentParser(
        description="Function calling with LLMs"
    )
    argument_parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
        help="Path to the input prompts JSON file"
    )
    argument_parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
        help="Path to the function definitions JSON file"
    )
    argument_parser.add_argument(
        "--output",
        default="data/output/function_calling_results.json",
        help="Path to the output JSON file"
    )
    return argument_parser.parse_args()


def main() -> None:
    """Load the input data, generate function calls
    with the language model and save the results."""
    args = parse_arguments()
    try:
        prompts, functions = parser(
            args.input,
            args.functions_definition)
        handler = LLMHandler()
        handler.load_model()
        results = []
        start_total = time.perf_counter()
        for prompt_data in prompts:
            start_prompt = time.perf_counter()
            prompt = build_prompt(functions, prompt_data.prompt)
            machine = StateMachine(functions)
            print(prompt_data.prompt)
            encoded = handler.encode_prompt(prompt)
            generated_text = ""
            while True:
                logits = np.array(handler.get_logits(encoded), dtype=float)
                while True:
                    next_id = int(np.argmax(logits))
                    if logits[next_id] == -np.inf:
                        raise NoValidTokenError("No valid tokens available")
                    token_text = handler.decode_prompt([next_id])
                    candidate_machine = copy.deepcopy(machine)
                    if candidate_machine.add_generated_text(token_text):
                        machine = candidate_machine
                        encoded.append(next_id)
                        generated_text += token_text
                        print(generated_text)
                        break
                    else:
                        logits[next_id] = -np.inf
                try:
                    result = json.loads(generated_text)
                    if isinstance(result, dict):
                        break
                except json.JSONDecodeError:
                    pass
            result = {"prompt": prompt_data.prompt, **result}
            results.append(result)
            print("JSON generado:", result)
            prompt_time = time.perf_counter() - start_prompt
            print(f"Prompt generation time: {prompt_time:.2f} seconds\n")
        total_time = time.perf_counter() - start_total
        print(f"\nTotal generation time: {total_time:.2f} seconds")
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4, ensure_ascii=False)
    except FileNotFoundError as e:
        print(f"Error: file not found: {e.filename}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(
            f"Error: invalid JSON in input file "
            f"(line {e.lineno}, column {e.colno}): {e.msg}")
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: input data does not match the expected structure.\n{e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: invalid input structure: {e}")
        sys.exit(1)
    except NoValidTokenError as e:
        print(f"Error during generation: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
