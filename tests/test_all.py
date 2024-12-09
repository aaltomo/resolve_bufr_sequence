#!/usr/bin/env python3

from resolve_bufr_sequence.resolve_bufr_sequence import read_sequence

def test_read():
    template = read_sequence("302046")
    assert template == { "302046": [ "004024", "004024", "012049" ] }
