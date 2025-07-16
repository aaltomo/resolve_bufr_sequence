#!/usr/bin/env python3
"""
Formatting utilities for BUFR sequence resolution.
Handles display formatting with color coding.
"""

import json
from typing import Any, Dict, List

from .io_utils import reader


class BColors:
    """ANSI color codes for terminal output."""

    PURPLE = "\033[95m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    EOC = "\033[0m"  # End of color


class Formatter:
    """Formatter for BUFR sequence data display."""

    def format_json(self, data: Dict[str, Any]) -> str:
        """Format data as JSON string."""
        return json.dumps(data, indent=4)

    def print_sequence(self, data: Dict[str, Any], show_as_json: bool) -> None:
        """Print sequence data either as JSON or formatted text."""
        if show_as_json:
            print(self.format_json(data))
        else:
            self.print_descriptor(data)

    def print_descriptor(self, desc_dict: Dict[str, List[Any]]) -> None:
        """
        Print the descriptor dictionary recursively.
        Formats different types of descriptors with different colors.
        """
        for key, values in desc_dict.items():
            self.print_blue(key)  # Descriptor dict key
            for value in values:
                if isinstance(value, str):
                    self.print_content(value)
                else:
                    self.print_descriptor(value)  # Recursively process nested dictionaries

    def print_content(self, template: str) -> None:
        """
        Print sequence, operator, replication or element with appropriate formatting.
        """
        if template.startswith("2"):  # Operator
            self.print_red(template)
        elif template.startswith("1"):  # Repeater
            self.print_purple(template)
        elif template.startswith("0") and len(template) > 1:  # Element
            self.print_element(template)
        else:
            print(f"No match for {template}? Strange.")

    def print_element(self, descriptor: str) -> None:
        """
        Print the final BUFR element details.
        """
        element_data = reader.read_descriptor(descriptor)
        if not element_data:
            print(f"Descriptor: {descriptor} not found.")
        else:
            self.print_green(element_data)

    def print_centre(self, centre_id: str) -> None:
        """
        Print the centre details.
        """
        centre_data = reader.read_centre(centre_id)
        if centre_data:
            self.print_purple(centre_data)
        else:
            print(f"Centre ID: {centre_id} not found.")

    def print_green(self, txt: List[str]) -> None:
        """Print with green color."""
        print(f"{BColors.GREEN}\t{txt[0]}{BColors.EOC} --> {txt[1]}")

    def print_red(self, txt: str) -> None:
        """Print with red color."""
        print(f"{BColors.RED}  {txt}{BColors.EOC}")

    def print_purple(self, txt: str) -> None:
        """Print with purple color."""
        print(f"{BColors.PURPLE}    {txt}{BColors.EOC}")

    def print_blue(self, txt: str) -> None:
        """Print with blue color."""
        print(f"{BColors.BLUE}[{txt}]{BColors.EOC}")


# Global formatter instance
formatter = Formatter()
