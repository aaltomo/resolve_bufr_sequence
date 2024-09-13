#!/usr/bin/env python3
"""
Resolve a bufr sequence aka. find out what elements
should occur in BUFR template/sequence. Needs eccodes library
installed in order to work.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List

already_read = []  # type: List[str]
# CODES_VERSION = "2.37.0"  # Latest from brew
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


def resolve_sequence(sequence: str, minimum: bool) -> None:
    """
    Resolve a BUFR sequence. Omit sequences that have already printed.
    """
    if sequence in already_read:
        pass
    else:
        if not minimum:
            print(f"{bcolors.BLUE}[{sequence}]{bcolors.EOC}")
        already_read.append(sequence)
        template = read_sequence(sequence)
        if not template:
            print(f"Nothing found for sequence: {sequence}")
            sys.exit(0)
        for t in template:
            print(f"{bcolors.BLUE}[{t}]{bcolors.EOC}") if minimum else print_content(t, minimum)


def read_sequence(sequence: str) -> List[str]:
    """
    Read BUFR sequence number from line.
    Can include other sequences.
    Example from file:
    "301022" = [  005001, 006001, 007001 ]
    """
    endchar = "]"  # read until char, can be on the next line
    elements = []
    try:
        with Path(SEQUENCE_FILE).open("r") as fp:
            goto_next_line = False
            for line in fp:
                if goto_next_line:
                    result = re.split(r"\W+", line)
                    for n in result:
                        elements.append(n)
                if endchar in line:
                    goto_next_line = False
                if re.match(rf"^\"{sequence}\" =", line):  # match sequence
                    result = re.split(r"\W+", line)
                    for n in result:
                        elements.append(n)
                    goto_next_line = False if endchar in line else True
            elements = list(filter(None, elements))  # Remove empty
            return elements
    except FileNotFoundError:
        print("Cannot find eccodes files. Is the library installed?")
        sys.exit(1)


def print_content(templ: str, minimum: bool) -> None:
    """
    Print sequence, operator, replication or element
    """
    if templ.startswith(str(3)) and len(templ) == 6:  # e.g. 307080
        resolve_sequence(templ, minimum)  # We need to go deeper
    elif templ.startswith(str(2)):
        print(f"{bcolors.RED}  [{templ}]{bcolors.EOC}")
    elif templ.startswith(str(1)):  # Repeater
        print(f"{bcolors.PURPLE}    [{templ}]{bcolors.EOC}")
    elif templ.startswith(str(0)) and len(templ) > 1:
        print_descr(templ)
    else:
        print(f"No match for {templ}? Strange.")


def print_descr(descr: str) -> None:
    """
    Print the final bufr element (eccodes key). No more inner levels.
    Example:
    007002|height|long|HEIGHT OR ALTITUDE|m|-1|-40|16|m|-1|5
    """
    final = ""
    with Path(ELEMENT_FILE).open("r") as f:
        for line in f:
            if re.match(descr, line):  # match descriptor
                final = line.split("|")
                break
        if not final:
            print(f"Descriptor: {descr} not found?")
        else:
            print(f"{bcolors.GREEN}\t{final[0]}{bcolors.EOC} --> {final[1]}")


def print_centre(centre_id: str) -> None:
    """
    Print the centre
    """
    with Path(CENTRE_FILE).open("r") as f:
        for line in f:
            if re.match(centre_id, line):  # match descriptor
                print(f"{bcolors.GREEN}{line}{bcolors.EOC}")
                break


def resolve_bufr_sequence() -> None:
    # Paths to eccodes sequences and elements

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sequence", help="BUFR sequence to decode (e.g. 307080)")
    parser.add_argument("-d", "--descriptor", help="BUFR descriptor to decode (e.g. 007001)")
    parser.add_argument("-c", "--centre", help="BUFR centre to decode")
    parser.add_argument(
        "-m",
        "--minimum",
        help="Just show what table entries the sequence includes. Don't resolve values.",
        action="store_true",
    )

    args = parser.parse_args(args=None if sys.argv[1:] else ["-h"])
    minimum = False if not args.minimum else True

    if args.sequence:
        print(f"Using: {ROOT} with WMO tables {WMO_TABLE_NUMBER}.")
        print(f"Sequence -->")
        resolve_sequence(args.sequence, minimum)
    elif args.descriptor:
        print_content(args.descriptor, minimum)
    elif args.centre:
        print_centre(args.centre)


if __name__ == "__main__":
    resolve_bufr_sequence()
