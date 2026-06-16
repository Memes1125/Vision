# labelImg в проекте vision (Windows)

## Установка (один раз)

```bat
scripts\setup_labelimg.bat
```

Окружение ставится в `%LOCALAPPDATA%\vision\venv` — обычный `pip install`, но не в папку проекта: **PyQt5 на Windows падает**, если путь к venv содержит кириллицу (у вас проект в `Все Работы\Курсор\...`).

На **Python 3.12+** нужен `setuptools` (уже в `requirements-label.txt`).

## Запуск

**Двойной клик:** `scripts\run_labelimg.bat`

**Или из PowerShell:**

```powershell
& "$env:LOCALAPPDATA\vision\venv\Scripts\labelImg.exe"
```

С папкой кадров и списком классов:

```powershell
& "$env:LOCALAPPDATA\vision\venv\Scripts\labelImg.exe" dataset\images dataset\classes.txt
```

Пример `classes.txt` для мишеней:

```text
target_8
target_9
hole
```

## Формат YOLO в labelImg

1. Меню **View → Auto Save** — сохранять `.txt` автоматически.
2. Слева переключатель **PascalVOC → YOLO** (должно быть **YOLO**).
3. **W** — новый bbox, **D** — следующий кадр, **A** — предыдущий.

Разметка: один `.txt` на каждое изображение, те же имена, что у `.jpg`/`.png`.

## Папка датасета (рекомендация)

```text
dataset/
  images/          ← открыть эту папку в labelImg
  labels/          ← сюда попадут .txt (настройте Save Dir в программе)
  classes.txt
```

В labelImg: **Change Save Dir** → `dataset\labels`, **Open Dir** → `dataset\images`.
