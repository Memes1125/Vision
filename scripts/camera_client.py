"""
Клиент: забирает кадры с ПК, где запущен camera_server.py (камеры подключены там).

  python scripts/camera_client.py --host 192.168.0.43

Сохранить снимки:
  python scripts/camera_client.py --host 192.168.0.43 --save-dir dataset\\images --once

Показать в окне (три камеры + общий кадр):
  python scripts/camera_client.py --host 192.168.0.43 --view
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def fetch_jpeg(host: str, port: int, path: str, timeout: float = 5.0) -> bytes:
    url = f"http://{host}:{port}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "vision-camera-client/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def jpeg_to_bgr(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Не удалось декодировать JPEG")
    return img


def list_cameras(host: str, port: int) -> list[int]:
    url = f"http://{host}:{port}/list"
    with urllib.request.urlopen(url, timeout=5.0) as resp:
        text = resp.read().decode("utf-8")
    # простой разбор {"cameras": [0, 1, 2]}
    import json

    return list(json.loads(text)["cameras"])


def save_frames(host: str, port: int, cameras: list[int], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    for cam in cameras:
        data = fetch_jpeg(host, port, f"/cam/{cam}.jpg")
        path = out_dir / f"{ts}_cam{cam}.jpg"
        path.write_bytes(data)
        print(f"Сохранено: {path}")
    try:
        data = fetch_jpeg(host, port, "/cam/all.jpg")
        path = out_dir / f"{ts}_all.jpg"
        path.write_bytes(data)
        print(f"Сохранено: {path}")
    except urllib.error.HTTPError:
        pass


def view_loop(host: str, port: int, cameras: list[int], interval: float) -> None:
    while True:
        tiles = []
        for cam in cameras:
            try:
                data = fetch_jpeg(host, port, f"/cam/{cam}.jpg")
                img = jpeg_to_bgr(data)
                cv2.putText(
                    img,
                    f"cam {cam}",
                    (8, 24),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                tiles.append(img)
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
                print(f"cam {cam}: {e}", file=sys.stderr)
        if tiles:
            h = max(t.shape[0] for t in tiles)
            row = []
            for t in tiles:
                scale = h / t.shape[0]
                w = max(1, int(t.shape[1] * scale))
                row.append(cv2.resize(t, (w, h)))
            vis = np.hstack(row)
            cv2.imshow("cameras-remote", vis)
        key = cv2.waitKey(max(1, int(interval * 1000))) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            save_frames(host, port, cameras, Path("captures"))
    cv2.destroyAllWindows()


def main() -> None:
    ap = argparse.ArgumentParser(description="Клиент: кадры с ПК camera_server.")
    ap.add_argument("--host", default="192.168.0.43", help="IP ПК с камерами.")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument(
        "--cameras",
        default=None,
        help="Индексы через запятую; по умолчанию — запрос /list с сервера.",
    )
    ap.add_argument("--save-dir", type=Path, default=None, help="Папка для сохранения JPEG.")
    ap.add_argument("--once", action="store_true", help="Один проход и выход (с --save-dir).")
    ap.add_argument("--view", action="store_true", help="Показать поток в окне OpenCV.")
    ap.add_argument("--interval", type=float, default=0.15, help="Пауза между кадрами (сек).")
    args = ap.parse_args()

    if args.cameras:
        cameras = [int(x.strip()) for x in args.cameras.split(",") if x.strip()]
    else:
        try:
            cameras = list_cameras(args.host, args.port)
        except Exception as e:
            print(f"Не удалось подключиться к {args.host}:{args.port} — {e}", file=sys.stderr)
            print("На ПК с камерами запустите: python scripts/camera_server.py", file=sys.stderr)
            sys.exit(1)

    print(f"Сервер: http://{args.host}:{args.port}  камеры: {cameras}")

    if args.view:
        view_loop(args.host, args.port, cameras, args.interval)
        return

    if args.save_dir:
        if args.once:
            save_frames(args.host, args.port, cameras, args.save_dir)
        else:
            print("Сохранение по кругу. Клавиша: Ctrl+C")
            try:
                while True:
                    save_frames(args.host, args.port, cameras, args.save_dir)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nГотово.")
        return

    # по умолчанию — один снимок в captures/
    out = Path("captures")
    save_frames(args.host, args.port, cameras, out)
    print("Подсказка: --view для просмотра, --save-dir dataset/images --once для датасета")


if __name__ == "__main__":
    main()
