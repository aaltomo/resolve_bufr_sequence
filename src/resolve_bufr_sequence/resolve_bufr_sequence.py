#!/usr/bin/env python3
"""
Resolve a bufr sequence aka. find out what elements
should occur in BUFR template/sequence. Needs eccodes library
installed in order to work.
"""

import re
import sys
import argparse
import json
from pathlib import Path
from typing import Any


# CODES_VERSION = "2.39.0"  # Latest from brew
# ROOT = f"/opt/homebrew/Cellar/eccodes/{CODES_VERSION}/share/eccodes/definitions/bufr/tables/0/wmo"
ROOT = "/usr/share/eccodes/definitions/bufr/tables/0/wmo"
WMO_TABLE_NUMBER = "37"  # latest atm.
SEQUENCE_FILE = f"{ROOT}/{WMO_TABLE_NUMBER}/sequence.def"
ELEMENT_FILE = f"{ROOT}/{WMO_TABLE_NUMBER}/element.table"
CENTRE_FILE = f"{ROOT}/{WMO_TABLE_NUMBER}/codetables/1033.table"


class bcolors:
    PURPLE = "\033[95m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    EOC = "\033[0m"


def resolve_sequence(sequence: str, show_as_json: bool) -> None:
    """
    Resolve a BUFR sequence. Omit sequences that have already printed.
    """
    data: dict[str, Any] = read_sequence(sequence)
    if show_as_json:
        print(json.dumps(data, indent=4))
    else:
        resolve_descriptor(data)


def resolve_descriptor(desc_dict: dict[str, list[str]]) -> None:
    """
    Resolve the final descriptor. Recursive if item is a dict.
    """
    for key, val in desc_dict.items():
        print_blue(key)  # Descriptor dict key
        for v in val:
            if isinstance(v, str):
                print_content(v)
            else:
                resolve_descriptor(v)  # dict


def is_sequence(seq: str) -> bool:
    return True if seq.startswith("3") else False


def read_sequence(sequence_number: str) -> dict[str, Any]:
    """
    Read BUFR sequence number from line.
    Can include other sequences(dicts). Function is recursive.
    Example from file:
    "301022" = [  005001, 006001, 007001 ]
    Return dict = {'301022': ["005001", "006001", "007001"]}
    """
    endchar: str = "]"  # read until char, can be on the next line
    elements: list[str | dict[str, Any]] = []
    elem_dict: dict[str, Any] = {}
    try:
        with Path(SEQUENCE_FILE).open("r") as fp:
            goto_next_line = False
            for line in fp:
                if goto_next_line:
                    result = re.split(r"\W+", line)
                    for n in result:
                        if is_sequence(n):  # can include other sequences
                            tmp = read_sequence(n)
                            elements.append(tmp)
                        else:
                            elements.append(n)
                if endchar in line:
                    goto_next_line = False
                if re.match(rf"^\"{sequence_number}\" =", line):  # match sequence
                    result = re.split(r"\W+", line)
                    for n in result:
                        if n != sequence_number:
                            if is_sequence(n):  # can include other sequences
                                tmp = read_sequence(n)
                                elements.append(tmp)
                            else:
                                elements.append(n)
                    goto_next_line = False if endchar in line else True
            elements = list(filter(None, elements))  # Remove empty
            elem_dict[sequence_number] = elements
            return elem_dict
    except FileNotFoundError:
        print("Cannot find eccodes files. Is the library installed?")
        sys.exit(1)


def print_green(txt: list[str]) -> None:
    print(f"{bcolors.GREEN}\t{txt[0]}{bcolors.EOC} --> {txt[1]}")


def print_red(txt: str) -> None:
    print(f"{bcolors.RED}  {txt}{bcolors.EOC}")


def print_purple(txt: str) -> None:
    print(f"{bcolors.PURPLE}    {txt}{bcolors.EOC}")


def print_blue(txt: str) -> None:
    print(f"{bcolors.BLUE}[{txt}]{bcolors.EOC}")


def print_content(templ: str) -> None:
    """
    Print sequence, operator, replication or element
    """

    if templ.startswith(str(2)):
        print_red(templ)
    elif templ.startswith(str(1)):  # Repeater
        print_purple(templ)
    elif templ.startswith(str(0)) and len(templ) > 1:
        print_descriptor(templ)
    else:
        print(f"No match for {templ}? Strange.")


def print_descriptor(descr: str) -> None:
    """
    Print the final bufr element (eccodes key). No more inner levels.
    Example:
    007002|height|long|HEIGHT OR ALTITUDE|m|-1|-40|16|m|-1|5
    """
    final: list[str] = []
    # print(f"Got desc: {descr}")
    with Path(ELEMENT_FILE).open("r") as f:
        for line in f:
            if re.match(descr, line):  # match descriptor
                final = line.split("|")
                break
        if not final:
            print(f"Descriptor: {descr} not found?")
        else:
            print_green(final)


def print_centre(centre_id: str) -> None:
    """
    Print the centre
    """
    with Path(CENTRE_FILE).open("r") as f:
        for line in f:
            if re.match(centre_id, line):  # match descriptor
                print_purple(line)
                break


def resolve_bufr_sequence() -> None:
    # Paths to eccodes sequences and elements

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sequence", help="BUFR sequence to decode (e.g. 307080)")
    parser.add_argument("-d", "--descriptor", help="BUFR descriptor to decode (e.g. 007001)")
    parser.add_argument("-c", "--centre", help="BUFR centre to decode")
    parser.add_argument(
        "-j",
        "--show_json",
        help="Show JSON version of table entries the sequence includes. Don't resolve values.",
        action="store_true",
    )

    args = parser.parse_args(args=None if sys.argv[1:] else ["-h"])
    show_json = False if not args.show_json else True

    if args.sequence:
        print(f"Using: {ROOT} with WMO tables {WMO_TABLE_NUMBER}.")
        print("Sequence -->")
        resolve_sequence(args.sequence, show_json)
    elif args.descriptor:
        print_descriptor(args.descriptor)
    elif args.centre:
        print_centre(args.centre)


if __name__ == "__main__":
    resolve_bufr_sequence()
