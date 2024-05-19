#!/usr/bin/env python3

import pytest

from resolve_bufr_sequence import read_sequence

@pytest.fixture
def test_read():
    template = read_sequence("307089")
    assert template == "[  307087, 307088 ]"
