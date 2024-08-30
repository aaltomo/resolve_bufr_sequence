#!/usr/bin/env python3

import pytest

from resolve_bufr_sequence.resolve_bufr_sequence import read_sequence

def test_read():
    template = read_sequence("307089")
    assert template == [ "307089", "307087", "307088" ]
