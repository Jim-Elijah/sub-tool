"""Tests for timestamp helpers."""

from __future__ import annotations

from sub_tool.timestamp import (
    lrc_tag_to_ms,
    ms_to_srt_timestamp,
    srt_start_to_lrc_tag,
    srt_timestamp_to_ms,
)


def test_srt_round_trip_ms() -> None:
    ts = "00:01:20,500"
    assert ms_to_srt_timestamp(srt_timestamp_to_ms(ts)) == ts


def test_srt_to_lrc_tag() -> None:
    assert srt_start_to_lrc_tag("00:01:20,000") == "[01:20.00]"


def test_lrc_tag_to_ms() -> None:
    assert lrc_tag_to_ms("[01:20.00]hello") == 80_000
    assert lrc_tag_to_ms("[00:15.00]x") == 15_000
