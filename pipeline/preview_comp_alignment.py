"""Approximate a preview clip's time window inside a native composition render.

This is evidence tooling for clip-to-composition mapping.  It does not publish a
mapping by itself: the caller must still bind the native project/composition and
retain a review state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def _duration_seconds(capture: cv2.VideoCapture) -> float:
    fps = capture.get(cv2.CAP_PROP_FPS)
    frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    if fps <= 0 or frames <= 0:
        raise ValueError("video duration is unavailable")
    return frames / fps


def sample_video(path: Path, interval_seconds: float = 0.2) -> tuple[np.ndarray, float]:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"cannot open video: {path}")
    duration = _duration_seconds(capture)
    samples: list[np.ndarray] = []
    for timestamp in np.arange(0.0, duration, interval_seconds):
        capture.set(cv2.CAP_PROP_POS_MSEC, float(timestamp * 1000.0))
        ok, frame = capture.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (96, 54), interpolation=cv2.INTER_AREA)
        gray = cv2.GaussianBlur(gray, (3, 3), 0).astype(np.float32)
        gray -= gray.mean()
        deviation = float(gray.std())
        if deviation > 1e-6:
            gray /= deviation
        samples.append(gray.reshape(-1))
    capture.release()
    if len(samples) < 2:
        raise ValueError(f"not enough readable frames: {path}")
    return np.stack(samples), duration


def align_samples(clip: np.ndarray, native: np.ndarray, interval_seconds: float) -> dict:
    if clip.ndim != 2 or native.ndim != 2 or clip.shape[1] != native.shape[1]:
        raise ValueError("clip and native samples must be compatible 2D arrays")
    if len(clip) > len(native):
        raise ValueError("clip is longer than native candidate")

    scores: list[float] = []
    for start in range(len(native) - len(clip) + 1):
        candidate = native[start : start + len(clip)]
        frame_correlations = np.mean(clip * candidate, axis=1)
        scores.append(float(np.median(frame_correlations)))

    order = np.argsort(scores)[::-1]
    best = int(order[0])
    runner_up = int(order[1]) if len(order) > 1 else best
    return {
        "startSecondsApprox": round(best * interval_seconds, 3),
        "endSecondsApprox": round((best + len(clip)) * interval_seconds, 3),
        "score": round(scores[best], 6),
        "runnerUpStartSecondsApprox": round(runner_up * interval_seconds, 3),
        "runnerUpScore": round(scores[runner_up], 6),
        "sampleIntervalSeconds": interval_seconds,
        "sampleCount": len(clip),
    }


def align_videos(clip_path: Path, native_path: Path, interval_seconds: float = 0.2) -> dict:
    clip, clip_duration = sample_video(clip_path, interval_seconds)
    native, native_duration = sample_video(native_path, interval_seconds)
    result = align_samples(clip, native, interval_seconds)
    result.update(
        {
            "clip": str(clip_path.resolve()),
            "nativeRender": str(native_path.resolve()),
            "clipDurationSeconds": round(clip_duration, 6),
            "nativeDurationSeconds": round(native_duration, 6),
            "status": "approximate_requires_review",
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clip", type=Path)
    parser.add_argument("native_render", type=Path)
    parser.add_argument("--interval", type=float, default=0.2)
    args = parser.parse_args()
    if args.interval <= 0:
        raise SystemExit("--interval must be greater than zero")
    print(json.dumps(align_videos(args.clip, args.native_render, args.interval), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
