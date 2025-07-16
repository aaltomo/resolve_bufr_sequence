"""
Resolve BUFR sequence package.
Finds out what elements should occur in BUFR template/sequence.
"""

from resolve_bufr_sequence.resolve_bufr_sequence import resolve_bufr_sequence
from resolve_bufr_sequence.io_utils import reader
from resolve_bufr_sequence.formatter import formatter
from resolve_bufr_sequence.config import config


def main() -> None:
    """Main entry point for the command-line interface."""
    resolve_bufr_sequence()


__all__ = ["resolve_bufr_sequence", "reader", "formatter", "config", "main"]
