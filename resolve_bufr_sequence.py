#!/usr/bin/env python3
"""
Resolve a bufr sequence aka. find out what elements
should occur in BUFR template/sequence. Needs eccodes library
installed in order to work.
"""
import re
import sys
import argparse

already_read = []


class bcolors:
    PURPLE = "\033[95m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    EOC = "\033[0m"


def resolve_sequence(sequence):
    """
    Resolve a BUFR sequence. Omit sequences that have already printed.
    """
    if sequence in already_read:
        pass
    else:
        print(f"{bcolors.BLUE}[{sequence}]{bcolors.EOC}")
        already_read.append(sequence)
        template = read_sequence(sequence)
        for t in template:
            print_content(t)


def read_sequence(sequence):
    """
    Read BUFR sequence number from line.
    Can include other sequences.
    """
    end = "]"  # read until char, can be on the next line
    elements = []
    with open(seqfile, "r") as fp:
        started = False
        for line in fp:
            if started:
                result = re.split(r"\W+", line)
                for n in result:
                    elements.append(n)
            if end in line:
                started = False
            if re.match(rf"^\"{sequence}\" =", line):  # match sequence
                result = re.split(r"\W+", line)
                for n in result:
                    elements.append(n)
                if end in line:  # Can end on the same line or next
                    started = False
                else:
                    started = True
        elements = list(filter(None, elements)) #  Remove empty
        return elements


def print_content(templ):
    """
    Print sequence, operator, replication or element
    """
    if templ.startswith(str(3)) and len(templ) == 6: #  e.g. 307080
        resolve_sequence(templ)  #  We need to go deeper
    elif templ.startswith(str(2)):
        print(f"{bcolors.RED}  [{templ}]{bcolors.EOC}")
    elif templ.startswith(str(1)): #  Repeater
        print(f"{bcolors.PURPLE}    [{templ}]{bcolors.EOC}")
    elif templ.startswith(str(0)) and len(templ) > 1:
        print_descr(templ)
    else:
        print(f"No match for {templ}? Strange.")


def print_descr(descr):
    """
    Print the final bufr element (eccodes key). No more inner levels.
    """
    with open(elementfile) as f:
        for line in f:
            if re.match(descr, line):  # match descriptor
                final = line.split("|")
                print(f"{bcolors.GREEN}\t{final[0]}{bcolors.EOC} --> {final[1]}")
                break


def print_centre(id):
    """
    Print the centre
    """
    with open(centrefile) as f:
        for line in f:
            if re.match(id, line):  # match descriptor
                print(f"{bcolors.GREEN}{line}{bcolors.EOC}")
                break


if __name__ == "__main__":
    # Paths to eccodes sequences and elements
    root = "/usr/local/share/eccodes/definitions/bufr/tables/"
    wmo_table_number = "36"  # latest
    seqfile = f"{root}/0/wmo/{wmo_table_number}/sequence.def"
    elementfile = f"{root}/0/wmo/{wmo_table_number}/element.table"
    centrefile = f"{root}/0/wmo/{wmo_table_number}/codetables/1033.table"

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sequence", help="BUFR sequence to decode (e.g. 307080)")
    parser.add_argument("-d", "--descriptor", help="BUFR descriptor to decode (e.g. 007001)")
    parser.add_argument("-c", "--centre", help="BUFR centre to decode")

    args = parser.parse_args()

    if args is None:
        sys.exit(1)

    if args.sequence:
        print(f"Using: {root} with WMO tables {wmo_table_number}.")
        resolve_sequence(args.sequence)
    elif args.descriptor:
        print_content(args.descriptor)
    elif args.centre:
        print_centre(args.centre)

    if len(sys.argv) == 1:
        print(f"usage: {sys.argv[0]} BUFR-sequence (e.g. 307080)")
        sys.exit(1)
