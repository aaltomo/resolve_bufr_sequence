#!/usr/bin/env python3
"""
I/O utilities for BUFR sequence resolution.
Handles file reading operations with caching.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from resolve_bufr_sequence.config import config


class FileCache:
    """Cache for file contents to avoid repeated file reads."""

    def __init__(self) -> None:
        self._file_cache: Dict[Path, List[str]] = {}

    def read_file_lines(self, file_path: Path) -> List[str]:
        """Read all lines from a file, using cache if available."""
        if file_path not in self._file_cache:
            try:
                with file_path.open("r") as f:
                    self._file_cache[file_path] = f.readlines()
            except FileNotFoundError:
                raise FileNotFoundError(f"Required file not found: {file_path}")

        return self._file_cache[file_path]

    def clear_cache(self) -> None:
        """Clear the file cache."""
        self._file_cache.clear()


class BUFRReader:
    """Reader for BUFR sequence and element files."""

    def __init__(self) -> None:
        self._cache = FileCache()
        # Keep track of sequences we've already read to avoid infinite recursion
        self._sequence_stack: Set[str] = set()

    def read_sequence(self, sequence_number: str) -> Dict[str, Any]:
        """
        Read BUFR sequence number from file.
        Can include other sequences (dicts). Function is recursive.

        Example from file:
        "301022" = [  005001, 006001, 007001 ]

        Returns:
        dict = {'301022': ["005001", "006001", "007001"]}
        """
        # Guard against circular references
        if sequence_number in self._sequence_stack:
            return {sequence_number: ["<circular reference>"]}

        self._sequence_stack.add(sequence_number)

        elements: List[Any] = []
        elem_dict: Dict[str, Any] = {sequence_number: elements}
        end_char: str = "]"  # read until char, can be on the next line

        try:
            lines = self._cache.read_file_lines(config.sequence_file)
            goto_next_line = False

            for line in lines:
                # Continue parsing next line if needed
                if goto_next_line:
                    result = re.split(r"\W+", line)
                    for n in result:
                        if self._is_sequence(n):  # can include other sequences
                            tmp = self.read_sequence(n)
                            elements.append(tmp)
                        elif n:  # Only append non-empty strings
                            elements.append(n)

                # Stop reading if we've found the end character
                if end_char in line:
                    goto_next_line = False

                # Start reading if we've found the sequence
                if re.match(rf"^\"{sequence_number}\" =", line):  # match sequence
                    result = re.split(r"\W+", line)
                    for n in result:
                        if n != sequence_number and n:  # Skip header itself and empty strings
                            if self._is_sequence(n):  # can include other sequences
                                tmp = self.read_sequence(n)
                                elements.append(tmp)
                            else:
                                elements.append(n)
                    goto_next_line = False if end_char in line else True

            # Remove empty elements
            elements = [e for e in elements if e]

            self._sequence_stack.remove(sequence_number)
            return elem_dict

        except FileNotFoundError as e:
            self._sequence_stack.remove(sequence_number)
            raise e

    def read_descriptor(self, descriptor: str) -> Optional[List[str]]:
        """
        Read descriptor details from element file.

        Example:
        007002|height|long|HEIGHT OR ALTITUDE|m|-1|-40|16|m|-1|5

        Returns the line split by '|' or None if not found.
        """
        lines = self._cache.read_file_lines(config.element_file)
        for line in lines:
            if re.match(descriptor, line):  # match descriptor
                return line.strip().split("|")
        return None

    def read_centre(self, centre_id: str) -> Optional[str]:
        """Read centre details from centre file."""
        lines = self._cache.read_file_lines(config.centre_file)
        for line in lines:
            if re.match(centre_id, line):  # match descriptor
                return line.strip()
        return None

    @staticmethod
    def _is_sequence(seq: str) -> bool:
        """Check if a string represents a sequence (starts with '3')."""
        return bool(seq and seq.startswith("3"))


# Global reader instance
reader = BUFRReader()
