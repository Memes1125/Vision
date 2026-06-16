# Vision

Разметка датасета, обучение YOLO и работа с камерами (Windows).

## Быстрый старт

### Разметка (labelImg)

```bat
scripts\setup_labelimg.bat
scripts\run_labelimg.bat dataset dataset\classes.txt
```

### YOLO

```bat
scripts\setup_yolo.bat
scripts\prepare_yolo_dataset.bat
scripts\train_yolo.bat
scripts\predict_yolo.bat --source dataset --save
```

### Камеры

```bat
scripts\run_camera_server.bat
scripts\run_camera_client.bat
```

Подробнее: [docs/labelimg.md](docs/labelimg.md), [docs/camera_network.md](docs/camera_network.md).

## Структура

- `dataset/` — кадры и YOLO-разметка (`.txt` + `classes.txt`)
- `scripts/` — установка, обучение, инференс, камеры
- `runs/train/` — обученная модель (`weights/best.pt`) и метрики
- `runs/predict/` — результаты инференса (локально, не в git)
- venv: `%LOCALAPPDATA%\vision\venv` (labelImg), `%LOCALAPPDATA%\vision\yolo-venv` (YOLO)
