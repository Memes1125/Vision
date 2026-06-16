"""Локальные USB-камеры с YOLO-инференсом по индексам (0, 1, 2, ...)."""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import cv2
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]

BACKENDS = {
    "dshow": cv2.CAP_DSHOW,
    "msmf": cv2.CAP_MSMF,
    "any": cv2.CAP_ANY,
}

BLACK_FRAME_MEAN = 20.0
WARMUP_FRAMES = 25


@dataclass
class OpenProfile:
    backend: int
    backend_label: str
    capture_width: int
    capture_height: int
    mjpeg: bool


def default_weights() -> Path:
    best = ROOT / "runs" / "train" / "weights" / "best.pt"
    if best.is_file():
        return best
    raise SystemExit(
        f"Нет обученной модели: {best}\n"
        "Сначала обучите: scripts\\prepare_yolo_dataset.bat  и  scripts\\train_yolo.bat"
    )


def parse_cameras(value: str) -> List[int]:
    indices = [int(x.strip()) for x in value.split(",") if x.strip()]
    if not indices:
        raise SystemExit("Укажите хотя бы одну камеру: --cameras 0 или --cameras 0,1,2")
    return indices


def is_black_frame(frame) -> bool:
    return float(frame.mean()) < BLACK_FRAME_MEAN


def warmup(cap: cv2.VideoCapture, frames: int = WARMUP_FRAMES) -> None:
    for _ in range(frames):
        cap.read()


def probe_camera(cap: cv2.VideoCapture) -> bool:
    warmup(cap)
    ok, frame = cap.read()
    return bool(ok and frame is not None and not is_black_frame(frame))


def resolve_profile(
    backend_name: str,
    camera_count: int,
    width: int,
    height: int,
    capture_width: Optional[int],
    capture_height: Optional[int],
    mjpeg: Optional[bool],
) -> OpenProfile:
    if backend_name == "auto":
        if camera_count > 1:
            return OpenProfile(
                backend=BACKENDS["dshow"],
                backend_label="dshow+mjpeg",
                capture_width=capture_width or 320,
                capture_height=capture_height or 240,
                mjpeg=True if mjpeg is None else mjpeg,
            )
        return OpenProfile(
            backend=BACKENDS["dshow"],
            backend_label="dshow",
            capture_width=capture_width or width,
            capture_height=capture_height or height,
            mjpeg=False if mjpeg is None else mjpeg,
        )

    backend = BACKENDS[backend_name]
    return OpenProfile(
        backend=backend,
        backend_label=backend_name,
        capture_width=capture_width or width,
        capture_height=capture_height or height,
        mjpeg=False if mjpeg is None else mjpeg,
    )


def open_camera(index: int, profile: OpenProfile) -> Optional[cv2.VideoCapture]:
    cap = cv2.VideoCapture(index, profile.backend)
    if not cap.isOpened():
        print(f"Камера {index} не открылась.", file=sys.stderr)
        cap.release()
        return None

    if profile.mjpeg and profile.backend == BACKENDS["dshow"]:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, profile.capture_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, profile.capture_height)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def open_cameras(
    indices: List[int],
    backend_name: str,
    width: int,
    height: int,
    open_delay: float,
    capture_width: Optional[int],
    capture_height: Optional[int],
    mjpeg: Optional[bool],
) -> tuple[List[Optional[cv2.VideoCapture]], OpenProfile]:
    profile = resolve_profile(
        backend_name,
        len(indices),
        width,
        height,
        capture_width,
        capture_height,
        mjpeg,
    )

    caps: List[Optional[cv2.VideoCapture]] = []
    for idx in indices:
        if open_delay > 0 and caps:
            time.sleep(open_delay)
        caps.append(open_camera(idx, profile))

    for i, cap in enumerate(caps):
        if cap is None:
            continue
        if not probe_camera(cap):
            print(
                f"Камера {indices[i]}: нет нормального кадра "
                f"({profile.backend_label} {profile.capture_width}x{profile.capture_height}).",
                file=sys.stderr,
            )
            cap.release()
            caps[i] = None

    return caps, profile


def main() -> None:
    parser = argparse.ArgumentParser(description="USB-камеры с YOLO по индексам.")
    parser.add_argument("--cameras", default="0,1,2", help="Индексы через запятую, например 0,1,2")
    parser.add_argument("--weights", type=Path, default=None, help="Путь к best.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--device", default="cpu", help="cpu или 0 для GPU")
    parser.add_argument("--width", type=int, default=640, help="Ширина окна и YOLO.")
    parser.add_argument("--height", type=int, default=480, help="Высота окна и YOLO.")
    parser.add_argument("--capture-width", type=int, default=None, help="Разрешение захвата.")
    parser.add_argument("--capture-height", type=int, default=None, help="Разрешение захвата.")
    parser.add_argument("--mjpeg", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--backend", default="auto", choices=("auto", "dshow", "msmf", "any"))
    parser.add_argument("--open-delay", type=float, default=0.3, help="Пауза между открытием камер.")
    args = parser.parse_args()

    weights = args.weights or default_weights()
    if not weights.is_file():
        raise SystemExit(f"Файл модели не найден: {weights}")

    indices = parse_cameras(args.cameras)
    model = YOLO(str(weights))

    caps, profile = open_cameras(
        indices,
        args.backend,
        args.width,
        args.height,
        args.open_delay,
        args.capture_width,
        args.capture_height,
        args.mjpeg,
    )

    win_names = [f"Camera {idx}" for idx in indices]
    for i, cap in enumerate(caps):
        if cap:
            cv2.namedWindow(win_names[i], cv2.WINDOW_NORMAL)
            cv2.resizeWindow(win_names[i], args.width, args.height)

    opened = [i for i, cap in enumerate(caps) if cap is not None]
    if not opened:
        raise SystemExit("Ни одна камера не открылась. Проверьте --cameras и подключение USB.")

    failed = [indices[i] for i in range(len(indices)) if caps[i] is None]
    if failed:
        print(f"Не открылись: {failed}", file=sys.stderr)

    print(f"Модель: {weights}")
    print(
        f"Захват: {profile.backend_label} {profile.capture_width}x{profile.capture_height}"
        + (" MJPEG" if profile.mjpeg else "")
    )
    print(f"Камеры: {[indices[i] for i in opened]}")
    print("Клавиша q — выход")

    try:
        while True:
            for i in opened:
                cap = caps[i]
                if cap is None or not cap.isOpened():
                    continue
                ok, frame = cap.read()
                if not ok or frame is None:
                    continue
                if is_black_frame(frame):
                    cv2.putText(
                        frame,
                        f"Camera {indices[i]}: black frame",
                        (16, 32),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                        cv2.LINE_AA,
                    )
                if frame.shape[1] != args.width or frame.shape[0] != args.height:
                    frame = cv2.resize(frame, (args.width, args.height))

                if not is_black_frame(frame):
                    results = model.predict(
                        frame,
                        conf=args.conf,
                        device=args.device,
                        verbose=False,
                    )
                    frame = results[0].plot()

                cv2.imshow(win_names[i], frame)

            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break
    finally:
        for cap in caps:
            if cap:
                cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
