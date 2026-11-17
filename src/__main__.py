import json
import sys
import argparse
import copy
import os
import time #eliminar esta linea al final
from pydantic import ValidationError
import numpy as np
from src.parser import parser
from src.instructions import build_prompt
from src.llm_handler import LLMHandler
from src.state_machine import StateMachine


def parse_arguments():
    argument_parser = argparse.ArgumentParser(
    description="Function calling with LLMs")
    argument_parser.add_argument(
    "--input",
    default="data/input/function_calling_tests.json",
    help="Path to the input prompts JSON file")
    argument_parser.add_argument(
    "--functions_definition",
    default="data/input/functions_definition.json",
    help="Path to the function definitions JSON file")
    argument_parser.add_argument(
    "--output",
    default="data/output/function_calling_results.json",
    help="Path to the output JSON file")
    return argument_parser.parse_args()

def main():
    args = parse_arguments()
    try:
        prompts, functions = parser(
            args.input,
            args.functions_definition)
        handler = LLMHandler()
        handler.load_model()
        results = []
        for prompt_data in prompts:
            prompt = build_prompt(functions, prompt_data.prompt)
            machine = StateMachine(functions)
            print(prompt)
            encoded = handler.encode_prompt(prompt)
            print("Tokens del prompt:", len(encoded)) #eliminar esta linea al final
            inference_time = 0.0 #eliminar esta linea al final
            generated_ids = []
            start_total = time.perf_counter() #eliminar esta linea al final
            generated_text = ""
            while True:
                start_token = time.perf_counter() #eliminar esta linea al final
                logits = np.array(handler.get_logits(encoded), dtype=float)
                token_time = time.perf_counter() - start_token #eliminar esta linea al final
                inference_time += token_time #eliminar esta linea al final
                print(f"Tiempo de inferencia: {token_time * 1000:.2f} ms")
                attempts = 0
                while True:
                    next_id = int(np.argmax(logits))
                    attempts += 1
                    token_text = handler.decode_prompt([next_id])
                    print(f"State: {machine.state} | Attempts: {attempts}")
                    candidate_machine = copy.deepcopy(machine)
                    if candidate_machine.add_generated_text(token_text):
                        machine = candidate_machine
                        encoded.append(next_id)
                        generated_ids.append(next_id)
                        generated_text += token_text
                        print(generated_text)
                        break
                    else:
                        print(
                        f"Rejected | State: {machine.state} | "
                        f"ID: {next_id} | "
                        f"Text: {repr(token_text)}"
                        )
                        logits[next_id] = -np.inf
                try:
                    result = json.loads(generated_text)
                    if isinstance(result, dict):
                        break
                except json.JSONDecodeError:
                    pass
            result["prompt"] = prompt_data.prompt
            results.append(result)
            print("JSON generado:", result)
            total_time = time.perf_counter() - start_total #eliminar esta linea al final
            print(f"\nTiempo total: {total_time:.3f} segundos") #eliminar esta linea al final
            print(f"Tokens generados: {len(generated_ids)}") #eliminar esta linea al final
            if generated_ids: #eliminar esta linea al final
                print(f"Tiempo medio de inferencia por token: " #eliminar esta linea al final
                f"{inference_time / len(generated_ids) * 1000:.2f} ms") #eliminar esta linea al final
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
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(130)

if __name__ == "__main__":
    main()
