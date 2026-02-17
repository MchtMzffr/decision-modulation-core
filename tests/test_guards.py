"""Tests for DMC guards."""

import pytest
from dmc_core.dmc.guards import (
    staleness_guard,
    liquidity_guard,
    spread_guard,
    exposure_guard,
    daily_loss_guard,
    cancel_rate_guard,
)


def test_staleness_guard_pass():
    ok, code = staleness_guard(1000, 1500, 1000)
    assert ok is True
    assert code == ""


def test_staleness_guard_fail():
    ok, code = staleness_guard(1000, 2500, 1000)
    assert ok is False
    assert code == "staleness_exceeded"


def test_liquidity_guard_pass():
    ok, _ = liquidity_guard(5.0, 1.0)
    assert ok is True


def test_liquidity_guard_fail():
    ok, code = liquidity_guard(0.5, 1.0)
    assert ok is False
    assert code == "liquidity_low"


def test_spread_guard_fail():
    ok, code = spread_guard(600.0, 500.0)
    assert ok is False
    assert code == "spread_wide"


def test_exposure_guard_fail():
    ok, code = exposure_guard(15.0, 10.0)
    assert ok is False
    assert code == "exposure_cap"


def test_daily_loss_guard_stop():
    ok, code = daily_loss_guard(-3.0, 2.5)
    assert ok is False
    assert code == "daily_loss_stop"


def test_cancel_rate_guard_throttle():
    ok, code = cancel_rate_guard(20, 20)
    assert ok is False
    assert code == "cancel_rate_throttle"
