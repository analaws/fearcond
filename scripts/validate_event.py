#!/usr/bin/env python3
"""
validate_event.py

Validate a JSONL file of atomic event records against a JSON Schema (Draft-07).
Requires: jsonschema

Example:
    pip install jsonschema
    python3 validate_event.py --input logs/session_0001/events.jsonl
"""

import argparse
import json
import sys
from jsonschema import Draft7Validator, RefResolver, exceptions as jsonschema_exceptions
from pathlib import Path
from typing import Any, Dict, Tuple

def load_schema(schema_path: Path) -> Dict[str, Any]:
    with schema_path.open('r', encoding='utf-8') as f:
        schema = json.load(f)
    return schema

def format_jsonpath(error) -> str:
    # Build a readable path for the error location
    path = ""
    for p in list(error.path):
        if isinstance(p, int):
            path += f"[{p}]"
        else:
            if path:
                path += "."
            path += str(p)
    return path or "(root)"

def validate_jsonl(schema_path: Path, input_path: Path, out_valid: Path = None,
                   stop_on_error: bool = False, verbose: bool = False) -> int:
    schema = load_schema(schema_path)
    resolver = RefResolver(base_uri=f"file://{schema_path.resolve()}", referrer=schema)
    validator = Draft7Validator(schema, resolver=resolver)

    total = 0
    valid_count = 0
    invalid_count = 0
    parse_errors = 0

    out_file = None
    if out_valid:
        out_file = open(out_valid, 'w', encoding='utf-8')

    with input_path.open('r', encoding='utf-8') as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                parse_errors += 1
                invalid_count += 1
                print(f"[PARSE ERROR] Line {lineno}: JSON decode error: {e.msg} (col {e.colno})")
                if verbose:
                    print(f"  Line content: {line}")
                if stop_on_error:
                    break
                continue

            errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
            if errors:
                invalid_count += 1
                print(f"[SCHEMA ERROR] Line {lineno}: {len(errors)} error(s)")
                for i, err in enumerate(errors, start=1):
                    jpath = format_jsonpath(err)
                    # Try to extract a human-friendly message
                    msg = err.message
                    validator_name = getattr(err.validator, "__name__", str(err.validator))
                    print(f"  {i}) Path: {jpath} | Validator: {err.validator} | Message: {msg}")
                    if verbose:
                        print(f"     Failed value: {err.instance!r}")
                if verbose:
                    print(f"  Line content: {json.dumps(obj, ensure_ascii=False)}")
                if stop_on_error:
                    break
            else:
                valid_count += 1
                if out_file:
                    out_file.write(json.dumps(obj, ensure_ascii=False) + "\n")

    if out_file:
        out_file.close()

    # Summary
    print("\nValidation summary")
    print("------------------")
    print(f"File: {input_path}")
    print(f"Schema: {schema_path}")
    print(f"Total records processed: {total}")
    print(f"Valid records: {valid_count}")
    print(f"Invalid records: {invalid_count}")
    print(f"Parse errors (invalid JSON): {parse_errors}")

    # Exit code: 0 if all valid, 1 if any invalid or parse errors
    return_code = 0 if (invalid_count == 0 and parse_errors == 0) else 1
    return return_code

def main():
    parser = argparse.ArgumentParser(description="Validate a JSONL event file against JSON Schema (Draft-07).")
    parser.add_argument("--schema", "-s", type=Path, default=Path("data_schema/event_schema.json"),
                        help="Path to JSON Schema file (default: data_schema/event_schema.json)")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Path to input JSONL file to validate")
    parser.add_argument("--out-valid", "-o", type=Path, default=None,
                        help="Optional path to write valid lines to a new JSONL file")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop on first parse or schema error")
    parser.add_argument("--verbose", action="store_true", help="Verbose output for invalid lines")

    args = parser.parse_args()

    schema_path = args.schema
    input_path = args.input

    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(2)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    try:
        exit_code = validate_jsonl(schema_path, input_path, out_valid=args.out_valid,
                                   stop_on_error=args.stop_on_error, verbose=args.verbose)
    except jsonschema_exceptions.SchemaError as se:
        print(f"Schema error while loading/validating schema: {se}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Unexpected error during validation: {e}", file=sys.stderr)
        raise

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
