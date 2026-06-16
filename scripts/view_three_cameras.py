"""
Три камеры через VDO.Ninja: открывает вкладки браузера и три окна-превью.

Запуск:
  python scripts/view_three_cameras.py

Клавиши в окнах:
  q — закрыть
  b — снова открыть вкладки браузера
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ─────────────────────────────────────────────
#  Вставьте сюда ваши view-ссылки с VDO.Ninja
# ─────────────────────────────────────────────
CAMERAS = [
    {"name": "Camera 1", "url": "https://vdo.ninja/v5/?view=8dCZqEv"},
    {"name": "Camera 2", "url": "https://vdo.ninja/v5/?view=qt9tscD"},
    {"name": "Camera 3", "url": None},   # ← вставьте URL третьей камеры
]
# ─────────────────────────────────────────────


def _stub_frame(name: str, url: Optional[str], w: int, h: int) -> np.ndarray:
    """Серый кадр-заглушка с URL и подсказками."""
    img = np.full((h, w, 3), 40, dtype=np.uint8)
    # цветная рамка
    cv2.rectangle(img, (4, 4), (w - 4, h - 4), (80, 80, 80), 2)
    lines = [
        name,
        "",
        "Видео идёт в браузере.",
        "Здесь будет YOLO-превью",
        "когда подключите модель.",
        "",
        "View URL:",
        (url or "--- не задан ---")[:72],
        "",
        "b — открыть браузер   q — выход",
    ]
    y = 40
    for i, line in enumerate(lines):
        color = (0, 220, 120) if i == 0 else (200, 200, 200) if line else (80, 80, 80)
        scale = 0.55 if i == 0 else 0.42
        cv2.putText(img, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
        y += 26 if i == 0 else 22
    return img


def open_browser_tabs() -> None:
    """Открыть вкладку для каждой камеры с заданным URL."""
    opened = 0
    for cam in CAMERAS:
        url = cam.get("url")
        if url:
            webbrowser.open_new_tab(url)
            print(f"  {cam['name']}: {url}")
            opened += 1
        else:
            print(f"  {cam['name']}: URL не задан — пропускаю")
    if opened == 0:
        print("Нет ни одного URL. Задайте их в CAMERAS в начале скрипта.")


def _fetch_http(host: str, port: int, cam_idx: int) -> Optional[np.ndarray]:
    url = f"http://{host}:{port}/cam/{cam_idx}.jpg"
    try:
        with urllib.request.urlopen(url, timeout=3.0) as r:
            data = r.read()
        arr = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Три камеры VDO.Ninja: браузер + OpenCV-превью.")
    ap.add_argument("--no-browser", action="store_true", help="Не открывать браузер автоматически.")
    ap.add_argument("--width",  type=int, default=640)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument(
        "--source",
        choices=("stub", "http", "local"),
        default="stub",
        help="stub — заглушка (по умолчанию); http — camera_server; local — USB на этом ПК.",
    )
    ap.add_argument("--host",    default="192.168.0.43")
    ap.add_argument("--port",    type=int, default=8765)
    ap.add_argument("--cameras", default="0,1,2", help="Индексы для --source http/local.")
    args = ap.parse_args()

    cam_indices: List[int] = [int(x) for x in args.cameras.split(",") if x.strip()]
    while len(cam_indices) < 3:
        cam_indices.append(len(cam_indices))

    # Открываем браузерные вкладки
    if not args.no_browser:
        print("Открываю вкладки браузера:")
        open_browser_tabs()
        print()

    # Создаём три окна OpenCV
    win_names = [cam["name"] for cam in CAMERAS]
    for name in win_names:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, args.width, args.height)

    # Локальные камеры (только если --source local)
    local_caps: List[Optional[cv2.VideoCapture]] = []
    if args.source == "local":
        for idx in cam_indices[:3]:
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                local_caps.append(cap)
            else:
                print(f"Камера {idx} не открылась.", file=sys.stderr)
                local_caps.append(None)

    print("Клавиши: q — выход, b — снова открыть браузер")

    try:
        while True:
            for i, cam in enumerate(CAMERAS):
                frame: Optional[np.ndarray] = None

                if args.source == "http":
                    frame = _fetch_http(args.host, args.port, cam_indices[i])
                elif args.source == "local" and i < len(local_caps):
                    cap = local_caps[i]
                    if cap and cap.isOpened():
                        ok, f = cap.read()
                        if ok and f is not None:
                            frame = f

                if frame is None:
                    frame = _stub_frame(cam["name"], cam.get("url"), args.width, args.height)
                elif frame.shape[1] != args.width or frame.shape[0] != args.height:
                    frame = cv2.resize(frame, (args.width, args.height))

                cv2.imshow(win_names[i], frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("b"):
                print("Открываю браузер:")
                open_browser_tabs()

            time.sleep(0.01)
    finally:
        for cap in local_caps:
            if cap:
                cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
