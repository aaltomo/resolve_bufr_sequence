#!/usr/bin/env python3

from src.resolve_bufr_sequence.io_utils import reader

def test_read():
    template = reader.read_sequence("302046")
    assert template == { "302046": [ "004024", "004024", "012049" ] }
