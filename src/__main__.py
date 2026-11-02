from src.parser import parser
from pydantic import ValidationError
import json
import sys


def main():
    try:
        parser()
    except FileNotFoundError as e:
        print(f"Error: file not found: {e.filename}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(
            f"Error: invalid JSON in input file "
            f"(line {e.lineno}, column {e.colno}): {e.msg}"
        )
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: input data does not match the expected structure.\n{e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: invalid input structure: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()
