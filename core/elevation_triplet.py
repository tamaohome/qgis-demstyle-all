from __future__ import annotations

from typing import Literal

ElevationSource = Literal["min", "mid", "max"]


def calculate_elevation_triplet(
    source: ElevationSource,
    min_value: int,
    mid_value: int,
    max_value: int,
    data_range: int,
) -> tuple[int, int, int]:
    """編集対象を起点に min/mid/max を再計算する。"""
    if source == "min":
        next_min = min_value
        next_mid = next_min + data_range
        next_max = next_mid + data_range
        return next_min, next_mid, next_max

    if source == "mid":
        next_mid = mid_value
        next_min = next_mid - data_range
        next_max = next_mid + data_range
        return next_min, next_mid, next_max

    next_max = max_value
    next_mid = next_max - data_range
    next_min = next_mid - data_range
    return next_min, next_mid, next_max
