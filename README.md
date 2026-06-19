# Vision

Разметка датасета, обучение YOLO и работа с USB-камерами (Windows).

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
scripts\train_yolo.bat --device cpu
scripts\predict_yolo.bat --source dataset --save --device cpu
```

### Камеры с обученной моделью

```bat
scripts\run_camera_yolo.bat --cameras 1,2,3
```

Индексы USB-камер: `0` — встроенная, `1–3` — USB, `4` — OBS Virtual Camera.

### Камеры по сети (опционально)

```bat
scripts\run_camera_server.bat
scripts\run_camera_client.bat --host 192.168.0.43 --view
```

Подробнее: [docs/labelimg.md](docs/labelimg.md), [docs/camera_network.md](docs/camera_network.md).

## Подробная инструкция по работе

Просто обучение 
```bat
scripts\train_yolo.bat
```

С нуля (рекомендуется при сильном росте датасета):
```bat
scripts\train_yolo.bat --model yolov8n.pt --epochs 100 --batch 4
```

Дообучение поверх старой модели (быстрее сходится):
```bat
scripts\train_yolo.bat --model runs\train\weights\best.pt --epochs 100 --batch 4
```

yolov8s.pt точнее, но дольше

## Структура

- `dataset/` — кадры и YOLO-разметка (`.txt` + `classes.txt`)
- `dataset_yolo/` — подготовленный датасет для обучения
- `scripts/` — установка, обучение, инференс, камеры
- `runs/train/` — обученная модель (`weights/best.pt`) и метрики
- `runs/predict/` — результаты инференса (локально, не в git)
- venv: `%LOCALAPPDATA%\vision\venv` (labelImg), `%LOCALAPPDATA%\vision\yolo-venv` (YOLO), `.venv` (камеры по сети)
