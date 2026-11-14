import json
import sys
import argparse
import time #eliminar esta linea al final
from pydantic import ValidationError
from src.parser import parser
from src.instructions import build_prompt
from src.llm_handler import LLMHandler


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
        print(prompts)
        print(functions)
        handler = LLMHandler()
        handler.load_model()
        prompt = build_prompt(functions, prompts[2].prompt)
        print(prompt)
        encoded = handler.encode_prompt(prompt)
        print("Tokens del prompt:", len(encoded)) #eliminar esta linea al final
        inference_time = 0.0 #eliminar esta linea al final
        generated_ids = []
        start_total = time.perf_counter() #eliminar esta linea al final
        for token_number in range(100): #eliminar token_number y sustituirlo por _ al final
            start_token = time.perf_counter() #eliminar esta linea al final
            logits = handler.get_logits(encoded)
            next_id = handler.get_best_token(logits)
            token_time = time.perf_counter() - start_token #eliminar esta linea al final
            inference_time += token_time #eliminar esta linea al final
            encoded.append(next_id)
            generated_ids.append(next_id)
            generated_text = handler.decode_prompt(generated_ids)
            print(f"Token {token_number + 1}: {token_time * 1000:.2f} ms") #eliminar esta linea al final
            print(generated_text)
            try:
                result = json.loads(generated_text)
                if isinstance(result, dict):
                    print("JSON completo:", result)
                    break
            except json.JSONDecodeError:
                pass
        total_time = time.perf_counter() - start_total #eliminar esta linea al final
        print(f"\nTiempo total: {total_time:.3f} segundos")
        print(f"Tokens generados: {len(generated_ids)}")
        if generated_ids:
            print(f"Tiempo medio de inferencia por token: "
            f"{inference_time / len(generated_ids) * 1000:.2f} ms")
        token_to_id = handler.load_vocabulary()
        id_to_token = {}
        for token, token_id in token_to_id.items():
            id_to_token[token_id] = token

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
