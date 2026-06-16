"""Патч labelImg 1.8.6 под Python 3.10+: float→int для PyQt5 (зум, рисование bbox)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

MARKER = "# vision-patch-py312"


def _venv_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise SystemExit("LOCALAPPDATA не найден")
    return Path(local) / "vision" / "venv"


def _patch_file(path: Path, replacements: list[tuple[str, str]]) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    original = text
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f"Не найден фрагмент в {path}:\n{old}")
        text = text.replace(old, new, 1)
    path.write_text(text + f"\n{MARKER}\n", encoding="utf-8")
    return original != text


def patch_labelimg(venv: Path | None = None) -> None:
    root = venv or _venv_root()
    site = root / "Lib" / "site-packages"
    labelimg = site / "labelImg" / "labelImg.py"
    canvas = site / "libs" / "canvas.py"

    if not labelimg.is_file():
        raise SystemExit(f"labelImg не установлен: {labelimg}")

    changed = False
    changed |= _patch_file(
        labelimg,
        [
            (
                "        bar.setValue(bar.value() + bar.singleStep() * units)",
                "        bar.setValue(int(bar.value() + bar.singleStep() * units))",
            ),
            (
                "        self.zoom_widget.setValue(value)",
                "        self.zoom_widget.setValue(int(value))",
            ),
            (
                "        h_bar.setValue(new_h_bar_value)\n        v_bar.setValue(new_v_bar_value)",
                "        h_bar.setValue(int(new_h_bar_value))\n        v_bar.setValue(int(new_v_bar_value))",
            ),
        ],
    )
    changed |= _patch_file(
        canvas,
        [
            (
                "            p.drawRect(left_top.x(), left_top.y(), rect_width, rect_height)",
                "            p.drawRect(int(left_top.x()), int(left_top.y()), int(rect_width), int(rect_height))",
            ),
            (
                "            p.drawLine(self.prev_point.x(), 0, self.prev_point.x(), self.pixmap.height())",
                "            p.drawLine(int(self.prev_point.x()), 0, int(self.prev_point.x()), int(self.pixmap.height()))",
            ),
            (
                "            p.drawLine(0, self.prev_point.y(), self.pixmap.width(), self.prev_point.y())",
                "            p.drawLine(0, int(self.prev_point.y()), int(self.pixmap.width()), int(self.prev_point.y()))",
            ),
        ],
    )

    if changed:
        print("labelImg пропатчен (зум Ctrl+колёсико, рисование bbox).")
    else:
        print("labelImg уже пропатчен.")


if __name__ == "__main__":
    venv = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    patch_labelimg(venv)
