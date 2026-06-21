"""Пути к обученным весам YOLO."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def latest_weights(root: Path = ROOT) -> Path | None:
    candidates = list(root.glob("runs/*/weights/best.pt"))
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)
