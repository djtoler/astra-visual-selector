#!/usr/bin/env python3
"""Rank native time offsets by foreground-card silhouette agreement.

This intentionally ignores picture content. It is review evidence only and never
publishes an exact mapping without an editor checkpoint.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def masks(path: Path, interval: float = 0.04) -> tuple[list[np.ndarray], float]:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"cannot open video: {path}")
    fps = capture.get(cv2.CAP_PROP_FPS)
    count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = count / fps
    values: list[np.ndarray] = []
    kernel = np.ones((3, 3), np.uint8)
    for second in np.arange(0.0, duration - 1e-9, interval):
        capture.set(cv2.CAP_PROP_POS_MSEC, float(second * 1000))
        ok, frame = capture.read()
        if not ok:
            break
        frame = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]
        mask = (((value > 24) & (saturation > 22)) | (value > 90)).astype(np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        values.append(mask)
    capture.release()
    if len(values) < 3:
        raise ValueError(f"not enough frames: {path}")
    return values, duration


def dice(left: np.ndarray, right: np.ndarray) -> float:
    total = int(left.sum() + right.sum())
    return 1.0 if total == 0 else float(2 * np.logical_and(left, right).sum() / total)


def rank_offsets(clip_path: Path, native_path: Path, interval: float = 0.04) -> dict:
    clip, clip_duration = masks(clip_path, interval)
    native, native_duration = masks(native_path, interval)
    if len(clip) > len(native):
        raise ValueError("clip is longer than native render")
    scores = []
    stride = max(1, round(0.12 / interval))
    for start in range(len(native) - len(clip) + 1):
        frame_scores = [dice(clip[index], native[start + index]) for index in range(0, len(clip), stride)]
        scores.append((float(np.median(frame_scores)), start))
    ordered = sorted(scores, reverse=True)
    selected = []
    separation = max(1, round(0.4 / interval))
    for score, start in ordered:
        if all(abs(start - prior[1]) >= separation for prior in selected):
            selected.append((score, start))
        if len(selected) == 8:
            break
    return {
        "status": "ranked_candidates_require_editor_confirmation",
        "clip": str(clip_path.resolve()),
        "nativeRender": str(native_path.resolve()),
        "clipDurationSeconds": round(clip_duration, 6),
        "nativeDurationSeconds": round(native_duration, 6),
        "sampleIntervalSeconds": interval,
        "candidates": [
            {
                "startSeconds": round(start * interval, 3),
                "endSeconds": round(start * interval + clip_duration, 3),
                "silhouetteDice": round(score, 6),
            }
            for score, start in selected
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("clip", type=Path)
    parser.add_argument("native", type=Path)
    parser.add_argument("--interval", type=float, default=0.04)
    args = parser.parse_args()
    print(json.dumps(rank_offsets(args.clip, args.native, args.interval), indent=2))


if __name__ == "__main__":
    main()
