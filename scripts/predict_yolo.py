"""Инференс YOLO: картинка, папка или камера."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ultralytics import YOLO

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from model_paths import latest_weights

ROOT = Path(__file__).resolve().parents[1]


def default_weights() -> Path:
    best = latest_weights(ROOT)
    if best is not None:
        return best
    return Path("yolov8n.pt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Инференс YOLO")
    parser.add_argument("--weights", type=Path, default=default_weights())
    parser.add_argument("--source", default=str(ROOT / "dataset"), help="jpg, папка, 0 для камеры")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--device", default="0")
    parser.add_argument("--save", action="store_true", help="Сохранить результаты в runs/predict")
    args = parser.parse_args()

    model = YOLO(str(args.weights))
    model.predict(
        source=args.source,
        conf=args.conf,
        device=args.device,
        save=args.save,
        project=str(ROOT / "runs"),
        name="predict",
        exist_ok=True,
    )


if __name__ == "__main__":
    main()
