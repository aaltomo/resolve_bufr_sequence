#!/usr/bin/env python3
"""
Resolve a BUFR sequence aka. find out what elements
should occur in BUFR template/sequence. Needs eccodes library
installed in order to work.
"""

import sys
import argparse
import json

from resolve_bufr_sequence.config import config
from resolve_bufr_sequence.io_utils import reader
from resolve_bufr_sequence.formatter import formatter


def resolve_sequence(sequence: str, show_as_json: bool) -> None:
    """
    Resolve a BUFR sequence and display the results.

    Args:
        sequence: The BUFR sequence number to resolve
        show_as_json: Whether to display the result as JSON
    """
    try:
        data = reader.read_sequence(sequence)
        formatter.print_sequence(data, show_as_json)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def resolve_bufr_sequence() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Resolve BUFR sequences, descriptors, and centres.")
    parser.add_argument("-s", "--sequence", help="BUFR sequence to decode (e.g. 307080)")
    parser.add_argument("-d", "--descriptor", help="BUFR descriptor to decode (e.g. 007001)")
    parser.add_argument("-c", "--centre", help="BUFR centre to decode")
    parser.add_argument(
        "-j",
        "--show_json",
        help="Show JSON version of table entries the sequence includes. Don't resolve values.",
        action="store_true",
    )
    parser.add_argument(
        "--config",
        help="Show configuration information",
        action="store_true",
    )

    args = parser.parse_args(args=None if sys.argv[1:] else ["-h"])

    # Show configuration if requested
    if args.config:
        print(json.dumps(config.to_dict(), indent=4))
        return

    # Process the requested operation
    if args.sequence:
        print(f"Using: {config.root_path} with WMO tables {config.wmo_table_number}.")
        print("Sequence -->")
        resolve_sequence(args.sequence, args.show_json)
    elif args.descriptor:
        formatter.print_element(args.descriptor)
    elif args.centre:
        formatter.print_centre(args.centre)


if __name__ == "__main__":
    resolve_bufr_sequence()
