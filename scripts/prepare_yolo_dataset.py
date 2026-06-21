"""Разбивка размеченного dataset/ в структуру YOLO train/val."""
from __future__ import annotations

import argparse
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def read_classes(classes_file: Path) -> list[str]:
    if not classes_file.is_file():
        raise SystemExit(f"Нет файла классов: {classes_file}")
    names = [line.strip() for line in classes_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not names:
        raise SystemExit(f"Файл классов пуст: {classes_file}")
    return names


def collect_pairs(source: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for image in sorted(source.iterdir()):
        if image.suffix.lower() not in IMAGE_EXTS:
            continue
        label = source / f"{image.stem}.txt"
        if not label.is_file():
            print(f"Пропуск без разметки: {image.name}", file=sys.stderr)
            continue
        pairs.append((image, label))
    return pairs


def write_data_yaml(target: Path, names: list[str]) -> Path:
    yaml_path = target / "data.yaml"
    dataset_root = target.resolve().as_posix()
    lines = [
        f"path: {dataset_root}",
        "train: images/train",
        "val: images/val",
        f"nc: {len(names)}",
        "names:",
    ]
    lines.extend(f"  {i}: {name}" for i, name in enumerate(names))
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def prepare(source: Path, target: Path, val_ratio: float, seed: int) -> Path:
    names = read_classes(source / "classes.txt")
    pairs = collect_pairs(source)
    if not pairs:
        raise SystemExit(f"В {source} нет пар image+txt")

    if target.exists():
        shutil.rmtree(target)

    for split in ("train", "val"):
        (target / "images" / split).mkdir(parents=True)
        (target / "labels" / split).mkdir(parents=True)

    rng = random.Random(seed)
    rng.shuffle(pairs)
    val_count = max(1, int(len(pairs) * val_ratio)) if len(pairs) > 1 else 0

    for index, (image, label) in enumerate(pairs):
        split = "val" if index < val_count else "train"
        shutil.copy2(image, target / "images" / split / image.name)
        shutil.copy2(label, target / "labels" / split / label.name)

    yaml_path = write_data_yaml(target, names)
    print(f"Кадров: {len(pairs)} (train={len(pairs) - val_count}, val={val_count})")
    print(f"Классы: {', '.join(names)}")
    print(f"Конфиг: {yaml_path}")
    return yaml_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Подготовка датасета YOLO из dataset/")
    parser.add_argument("--source", type=Path, default=ROOT / "dataset")
    parser.add_argument("--target", type=Path, default=ROOT / "dataset_yolo")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    prepare(args.source.resolve(), args.target.resolve(), args.val_ratio, args.seed)


if __name__ == "__main__":
    main()
