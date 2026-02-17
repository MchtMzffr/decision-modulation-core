"""Tests for PacketV2 schema."""

import pytest
from dmc_core.schema import PacketV2


def test_packet_v2_to_dict():
    p = PacketV2(
        run_id="run-1",
        step=0,
        input={"ts": 1000},
        external={"mid": 0.5},
        mdm={"action": "QUOTE"},
        final_action={"action": "QUOTE"},
        latency_ms=2,
        mismatch=None,
    )
    d = p.to_dict()
    assert d["run_id"] == "run-1"
    assert d["step"] == 0
    assert d["latency_ms"] == 2
    assert "input" in d and "external" in d
