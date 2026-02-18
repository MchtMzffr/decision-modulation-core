# Decision Ecosystem — decision-modulation-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""
Legacy domain metrics — example only. Not part of core.
"""

from __future__ import annotations

import bisect
import numpy as np
from typing import Any


def _mid_at(ts_ms: int, mid_series: list[tuple[int, float]]) -> float:
    if not mid_series:
        return 0.0
    times = [t for t, _ in mid_series]
    idx = bisect.bisect_right(times, ts_ms) - 1
    if idx < 0:
        return mid_series[0][1]
    return mid_series[idx][1]


def adverse_selection_avg_ticks(
    fill_records: list[dict[str, Any]],
    mid_series: list[tuple[int, float]],
    horizon_ms: int,
    tick_size: float,
) -> float:
    if not fill_records or tick_size <= 0:
        return 0.0
    eps = 1e-12
    total_w = 0.0
    weighted_adv = 0.0
    for rec in fill_records:
        fill_ts_ms = rec.get("fill_ts_ms", 0)
        fill_mid = rec.get("fill_mid", 0.0)
        side = (rec.get("side") or "bid").lower()
        qty = rec.get("qty", 1.0)
        mid_after = _mid_at(fill_ts_ms + horizon_ms, mid_series)
        if side in ("bid", "buy", "long"):
            adv = max(0.0, (fill_mid - mid_after) / tick_size)
        else:
            adv = max(0.0, (mid_after - fill_mid) / tick_size)
        weighted_adv += adv * qty
        total_w += qty
    return weighted_adv / (total_w + eps)


def adverse_selection_avg(
    fill_records: list[dict[str, Any]],
    step_mid: dict[int, float],
    horizon_steps: int = 15,
) -> float:
    if not fill_records:
        return 0.0
    adverse: list[float] = []
    for rec in fill_records:
        step = rec.get("step", 0)
        side = rec.get("side", "bid")
        mid_fill = rec.get("mid_fill", 0.0)
        mid_later = step_mid.get(step + horizon_steps, mid_fill)
        if side == "ask":
            adverse.append(mid_later - mid_fill)
        else:
            adverse.append(mid_fill - mid_later)
    return float(np.mean(np.abs(adverse))) if adverse else 0.0


def max_drawdown(equity_curve: list[float]) -> float:
    if not equity_curve:
        return 0.0
    arr = np.array(equity_curve, dtype=float)
    peak = np.maximum.accumulate(arr)
    dd = peak - arr
    return float(np.max(dd)) if len(dd) else 0.0


def returns_from_equity_curve(equity_curve: list[float]) -> list[float]:
    if len(equity_curve) < 2:
        return []
    arr = np.array(equity_curve, dtype=float)
    return np.diff(arr).tolist()


def summary_stats(
    equity_curve: list[float],
    realized_pnl: float,
    action_counts: dict[str, int],
    latencies_ms: list[int],
    throttle_events: int = 0,
    error_count: int = 0,
) -> dict[str, Any]:
    final_equity = equity_curve[-1] if equity_curve else 0.0
    return {
        "final_equity": final_equity,
        "realized_pnl": realized_pnl,
        "max_drawdown": max_drawdown(equity_curve),
        "action_counts": action_counts,
        "avg_latency_ms": float(np.mean(latencies_ms)) if latencies_ms else 0.0,
        "throttle_events": throttle_events,
        "error_count": error_count,
    }
