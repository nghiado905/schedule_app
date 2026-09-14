# Thoi Khoa Bieu Mobile

Mobile timetable app built with Python, Flet, and local SQLite storage.

The app keeps data on the user's device. Lessons remain after closing and reopening the app, and are removed only when the user clears app data or uninstalls the app.

## Features

- Week calendar inspired by Fantastical/Figma layout
- Day, week, month, and year views
- Tap an empty time slot to create a lesson
- Long press and drag across time slots to create a longer lesson
- Edit and delete existing lessons
- Pick lesson color
- Local SQLite database per installed device
- Settings feature scaffold

## Project Structure

```text
android_app/
├─ main.py
├─ app.py
├─ constants.py
├─ models/
│  ├─ lesson.py
│  └─ settings.py
├─ repositories/
│  ├─ lesson_repository.py
│  └─ settings_repository.py
├─ components/
│  ├─ toolbar.py
│  ├─ sidebar.py
│  ├─ lesson_card.py
│  ├─ calendar_cell.py
│  └─ mode_button.py
├─ features/
│  ├─ calendar/
│  ├─ lessons/
│  └─ settings/
└─ utils/
   └─ date_utils.py
```

Architecture: `Feature-based UI + Layered Architecture`.

- `main.py`: app entrypoint
- `app.py`: app shell, shared state, navigation between views
- `components/`: small reusable UI pieces
- `features/`: complete user-facing features
- `models/`: app data classes
- `repositories/`: persistence layer for SQLite
- `utils/`: pure helper functions

## Run Locally

```powershell
cd D:\Sortdreams\tutoirial_dev\android_app

py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install flet

.\.venv\Scripts\flet.exe run main.py
```

## Build APK

Set environment variables:

```powershell
cd D:\Sortdreams\tutoirial_dev\android_app

$env:PYTHONUTF8="1"
$env:JAVA_HOME="C:\Users\Administrator\java\17.0.13+11"
$env:ANDROID_HOME="C:\Users\Administrator\Android\sdk"
```

Build APK:

```powershell
.\.venv\Scripts\flet.exe build apk --split-per-abi -v
```

Output:

```text
build\apk\thoi-khoa-bieu-arm64-v8a.apk
```

## Git Setup

Initialize repository:

```powershell
cd D:\Sortdreams\tutoirial_dev\android_app
git init
git add .
git commit -m "Initial Android timetable app"
```

Add remote later:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/thoi-khoa-bieu-mobile.git
git branch -M main
git push -u origin main
```

## Development Notes

When adding a new UI button, do not put all code directly in `app.py`.

Recommended flow:

```text
components/your_button.py
features/your_feature/your_feature.py
features/your_feature/your_dialog.py
```

Then connect it from `app.py`.

Example:

```python
self.settings = SettingsFeature(page)
...
self.settings.button()
```

This keeps the app easy to expand without turning `main.py` or `app.py` into a giant file.
