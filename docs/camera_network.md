# Камеры по сети (ПК 192.168.0.43)

## Схема

| ПК | IP (пример) | Роль |
|----|-------------|------|
| С камерами | **192.168.0.43** | `camera_server.py` — читает USB-камеры, отдаёт JPEG по HTTP |
| Ваш ПК | любой в той же сети | `camera_client.py` — скачивает картинки |

## 1. На ПК 192.168.0.43 (камеры подключены сюда)

```powershell
cd c:\Users\User\Desktop\vision
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python scripts\camera_server.py --host 0.0.0.0 --port 8765 --cameras 0,1,2
```

Или двойной клик: `scripts\run_camera_server.bat`

Проверка в браузере на этом же ПК: `http://127.0.0.1:8765/cam/0.jpg`

**Брандмауэр Windows:** разрешите входящие на порт **8765** (частная сеть), иначе с другого ПК не откроется.

## 2. На вашем ПК (клиент)

```powershell
.\.venv\Scripts\python scripts\camera_client.py --host 192.168.0.43
```

Сохранить в папку для разметки:

```powershell
.\.venv\Scripts\python scripts\camera_client.py --host 192.168.0.43 --save-dir dataset\images --once
```

Просмотр в окне (q — выход, s — сохранить кадр):

```powershell
.\.venv\Scripts\python scripts\camera_client.py --host 192.168.0.43 --view
```

Или: `scripts\run_camera_client.bat`

## URL сервера

- `http://192.168.0.43:8765/cam/0.jpg` — камера 0  
- `http://192.168.0.43:8765/cam/1.jpg` — камера 1  
- `http://192.168.0.43:8765/cam/all.jpg` — все камеры в один снимок  

## Если не подключается

1. `ping 192.168.0.43` с вашего ПК  
2. Сервер запущен на .43, в консоли нет ошибок камер  
3. Открыт порт 8765 в брандмауэре на .43  
4. Оба ПК в одной подсети (192.168.0.x)
