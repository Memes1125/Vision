"""
Сервер кадров с USB-камер. Запускать на ПК, к которому подключены камеры (например 192.168.0.43).

  python scripts/camera_server.py --host 0.0.0.0 --port 8765 --cameras 0,1,2

Клиент с другого ПК:
  python scripts/camera_client.py --host 192.168.0.43

В браузере снимок: http://192.168.0.43:8765/cam/0.jpg
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class CameraGrabber:
  def __init__(self, indices: List[int], width: int, height: int, backend: int) -> None:
    self.indices = indices
    self.width = width
    self.height = height
    self.backend = backend
    self._caps: Dict[int, cv2.VideoCapture] = {}
    self._frames: Dict[int, Optional[np.ndarray]] = {i: None for i in indices}
    self._lock = threading.Lock()
    self._stop = threading.Event()
    self._thread: Optional[threading.Thread] = None

  def start(self) -> None:
    for idx in self.indices:
      cap = cv2.VideoCapture(idx, self.backend)
      if not cap.isOpened():
        print(f"Предупреждение: камера {idx} не открылась", file=sys.stderr)
      else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
      self._caps[idx] = cap
    self._thread = threading.Thread(target=self._loop, daemon=True)
    self._thread.start()

  def _loop(self) -> None:
    while not self._stop.is_set():
      for idx in self.indices:
        cap = self._caps.get(idx)
        if cap is None or not cap.isOpened():
          continue
        ok, frame = cap.read()
        if ok and frame is not None:
          with self._lock:
            self._frames[idx] = frame
      time.sleep(0.01)

  def get_jpeg(self, cam: int, quality: int = 85) -> Optional[bytes]:
    with self._lock:
      frame = self._frames.get(cam)
    if frame is None:
      return None
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return buf.tobytes() if ok else None

  def get_mosaic_jpeg(self, quality: int = 85) -> Optional[bytes]:
    with self._lock:
      parts = [(i, self._frames.get(i)) for i in self.indices]
    imgs = [(i, f) for i, f in parts if f is not None]
    if not imgs:
      return None
    tiles = []
    for _, f in imgs:
      tiles.append(f)
    if len(tiles) == 1:
      mosaic = tiles[0]
    else:
      h = max(t.shape[0] for t in tiles)
      resized = []
      for t in tiles:
        scale = h / t.shape[0]
        w = max(1, int(t.shape[1] * scale))
        resized.append(cv2.resize(t, (w, h)))
      mosaic = cv2.hconcat(resized)
    ok, buf = cv2.imencode(".jpg", mosaic, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return buf.tobytes() if ok else None

  def stop(self) -> None:
    self._stop.set()
    if self._thread is not None:
      self._thread.join(timeout=2.0)
    for cap in self._caps.values():
      if cap.isOpened():
        cap.release()


def make_handler(grabber: CameraGrabber, indices: List[int]):
  class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
      print(f"[{self.address_string()}] {fmt % args}")

    def _send_bytes(self, data: bytes, content_type: str) -> None:
      self.send_response(200)
      self.send_header("Content-Type", content_type)
      self.send_header("Content-Length", str(len(data)))
      self.send_header("Cache-Control", "no-store")
      self.end_headers()
      self.wfile.write(data)

    def _send_json(self, text: str) -> None:
      data = text.encode("utf-8")
      self.send_response(200)
      self.send_header("Content-Type", "application/json; charset=utf-8")
      self.send_header("Content-Length", str(len(data)))
      self.end_headers()
      self.wfile.write(data)

    def do_GET(self) -> None:
      path = self.path.split("?", 1)[0]
      if path in ("/", "/help"):
        help_text = (
          "GET /cam/0.jpg  /cam/1.jpg  /cam/2.jpg  — снимок камеры\n"
          "GET /cam/all.jpg — все камеры в один кадр\n"
          "GET /list — список индексов\n"
        )
        self._send_bytes(help_text.encode("utf-8"), "text/plain; charset=utf-8")
        return
      if path == "/list":
        self._send_json('{"cameras": ' + str(indices) + "}")
        return
      if path == "/cam/all.jpg":
        data = grabber.get_mosaic_jpeg()
        if data is None:
          self.send_error(503, "No frames yet")
          return
        self._send_bytes(data, "image/jpeg")
        return
      if path.startswith("/cam/") and path.endswith(".jpg"):
        try:
          cam = int(path[5:-4])
        except ValueError:
          self.send_error(400, "Bad camera id")
          return
        if cam not in indices:
          self.send_error(404, "Camera not configured")
          return
        data = grabber.get_jpeg(cam)
        if data is None:
          self.send_error(503, "No frame")
          return
        self._send_bytes(data, "image/jpeg")
        return
      self.send_error(404, "Not found")

  return Handler


def main() -> None:
  ap = argparse.ArgumentParser(description="HTTP-сервер кадров с USB-камер (ПК с камерами).")
  ap.add_argument("--host", default="0.0.0.0", help="Слушать на всех интерфейсах (0.0.0.0).")
  ap.add_argument("--port", type=int, default=8765)
  ap.add_argument("--cameras", default="0,1,2", help="Индексы камер через запятую, например 0,1,2")
  ap.add_argument("--width", type=int, default=640)
  ap.add_argument("--height", type=int, default=480)
  ap.add_argument(
    "--backend",
    default="dshow",
    choices=("dshow", "msmf", "any"),
    help="Windows: dshow обычно стабильнее для нескольких USB-камер.",
  )
  args = ap.parse_args()

  indices = [int(x.strip()) for x in args.cameras.split(",") if x.strip()]
  if not indices:
    print("Укажите хотя бы одну камеру: --cameras 0", file=sys.stderr)
    sys.exit(1)

  backend_map = {
    "dshow": cv2.CAP_DSHOW,
    "msmf": cv2.CAP_MSMF,
    "any": cv2.CAP_ANY,
  }
  grabber = CameraGrabber(indices, args.width, args.height, backend_map[args.backend])
  grabber.start()

  Handler = make_handler(grabber, indices)
  server = ThreadingHTTPServer((args.host, args.port), Handler)
  print(f"Сервер камер: http://<IP_этого_ПК>:{args.port}/cam/0.jpg")
  print(f"Камеры: {indices}. Остановка: Ctrl+C")
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    print("\nОстановка...")
  finally:
    server.shutdown()
    grabber.stop()


def _log_fatal(exc: BaseException) -> None:
  import traceback

  msg = traceback.format_exc()
  log_path = Path(sys.executable).parent / "camera_server_log.txt" if getattr(sys, "frozen", False) else Path("camera_server_log.txt")
  try:
    log_path.write_text(msg, encoding="utf-8")
  except OSError:
    pass
  print("ERROR - camera_server crashed. See camera_server_log.txt in this folder.", file=sys.stderr)
  print(msg, file=sys.stderr)


if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    _log_fatal(e)
    sys.exit(1)
