# Камеры на ПК 192.168.0.43 без установки Python

На ПК с USB-камерами **не нужно ставить Python**. Достаточно скопировать **один файл `.exe`** (или portable FFmpeg).

---

## Вариант 1 (рекомендуется): `camera_server.exe`

Собирается **один раз** на вашем ПК, где уже есть Python и проект `vision`.

### Сборка (на вашем ПК)

```powershell
cd c:\Users\User\Desktop\vision
.\.venv\Scripts\pip install -r requirements.txt pyinstaller
scripts\build_camera_server_exe.bat
```

Готовая папка: **`dist\camera_server\`** (целиком, со всеми `.dll` — не только exe).

### На ПК 192.168.0.43

1. Скопируйте **всю папку** `camera_server` на флешке в `C:\vision_cam\` (внутри должен быть `camera_server.exe` и много файлов `_internal` или dll).
2. Скопируйте **`run_camera_server_exe.bat`** в эту же папку (из `dist\`).
2. Запускайте **`run_camera_server_exe.bat`** (не голый exe — bat покажет текст ошибки).
3. Если окно сразу закрылось — откройте в той же папке:
   - `server_out.log`
   - `camera_server_log.txt`
4. Частая причина на «чистом» Windows: нет **Visual C++ Redistributable x64**  
   https://aka.ms/v1/vs/17/release/vc_redist.x64.exe
5. Брандмауэр: разрешить **входящие TCP 8765** (частная сеть).

Никакого Python на .43 не требуется.

### С вашего ПК (как раньше)

```powershell
.\.venv\Scripts\python scripts\camera_client.py --host 192.168.0.43 --view
```

---

## Вариант 2: portable FFmpeg (без нашего exe)

1. Скачайте [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) — сборка `ffmpeg-release-essentials.zip`, распакуйте на .43 в `C:\ffmpeg\`.
2. Узнайте имена камер:
   ```cmd
   C:\ffmpeg\bin\ffmpeg.exe -list_devices true -f dshow -i dummy
   ```
3. Для каждой камеры — отдельное окно CMD с потоком MJPEG (порт свой):

   Камера 0, порт 8080 (пример — нужен простой HTTP-сервер; FFmpeg сам HTTP-сервер не поднимает удобно).

Поэтому для «только FFmpeg» чаще ставят **mediamtx.exe** (один файл, без установки) + FFmpeg пушит RTSP. Клиент: `rtsp://192.168.0.43:8554/cam0`.

Это сложнее в настройке, чем один `camera_server.exe`.

---

## Вариант 3: IP-камеры

USB остаются на .43, но если купить **сетевые камеры** — поток идёт напрямую по IP, ПК .43 для видео не нужен.

---

## Итог

| На .43 | Python | Сложность |
|--------|--------|-----------|
| `camera_server.exe` | Нет | Низкая |
| FFmpeg + mediamtx | Нет | Средняя |
| `python camera_server.py` | Да | Низкая (но вы не хотите) |
