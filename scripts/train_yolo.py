"""Обучение YOLOv8 на подготовленном датасете."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    from ultralytics import YOLO

    parser = argparse.ArgumentParser(description="Обучение YOLO (Ultralytics)")
    parser.add_argument("--data", type=Path, default=ROOT / "dataset_yolo" / "data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="Базовая модель, напр. yolov8n.pt / yolov8s.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=4, help="Меньше batch, если не хватает VRAM/памяти")
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="0 на Windows — иначе воркеры грузят torch повторно и падают по памяти",
    )
    parser.add_argument("--device", default="0", help="0 — GPU, cpu — без CUDA")
    parser.add_argument("--project", type=Path, default=ROOT / "runs")
    parser.add_argument("--name", default="train")
    args = parser.parse_args()

    data = args.data.resolve()
    if not data.is_file():
        raise SystemExit(f"Нет {data}. Сначала: scripts\\prepare_yolo_dataset.bat")

    model = YOLO(args.model)
    model.train(
        data=str(data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
        cache=False,
        device=args.device,
        project=str(args.project.resolve()),
        name=args.name,
        exist_ok=True,
    )


if __name__ == "__main__":
    main()
