# Project Structure: Reminder AI Pro

Reminder AI Pro is a multiplatform Desktop application built with Python that leverages AI to create structured reminders from natural language (voice or text).

# Intructions

Update this file whenever if necessary everytime the project is changed.

## 📁 File Tree

```text
Reminder/
├── .clinerules/
│   └── project_structure.md  # This file: Project architecture and file roles.
├── ai_handler.py             # AI logic: Audio transcription (Whisper) and NLP parsing (GPT-4o-mini).
├── database.py               # Data layer: SQLite persistence for reminders.
├── main.py                   # App entry point: CustomTkinter GUI and core orchestration.
├── pyproject.toml            # Dependency management (using 'uv').
├── README.md                 # Project overview and user instructions.
├── scheduler_handler.py      # Scheduling: Management of one-time and recurring jobs (APScheduler).
├── voice_recorder.py         # Hardware interface: Audio capture via sounddevice.
├── .env.sample               # Template for environment variables (OpenAI API Key).
└── reminders.db              # Local SQLite database (auto-generated).
```

## ⚙️ Core Modules & Purpose

### 1. `main.py` (The Orchestrator)
- Initializes the GUI using `CustomTkinter`.
- Manages the application lifecycle and UI state (e.g., recording toggle).
- Coordinates the flow of data between the Voice Recorder, AI Handler, Database, and Scheduler.
- Handles UI updates, notifications (`plyer`), and sound alerts (`pygame`).

### 2. `ai_handler.py` (The Brain)
- **Transcription**: Uses OpenAI's Whisper model to convert voice recordings into text.
- **Parsing**: Uses GPT-4o-mini to convert raw text (e.g., "Remind me to call John in 10 minutes") into structured JSON data including `text`, `trigger_type` (one-time/recurring), and `trigger_time`.

### 3. `scheduler_handler.py` (The Timer)
- Uses `APScheduler` (BackgroundScheduler) to manage background tasks.
- Supports:
    - **One-time**: Fixed date and time.
    - **Recurring**: Hourly, Daily, Weekly (specific days), and Monthly.
- Triggers a callback in `main.py` when a reminder is due.

### 4. `database.py` (The Memory)
- Simple SQLite wrapper to persist reminders.
- Stores: `id`, `text`, `trigger_type`, `trigger_time`, `recurring_params` (as JSON), and `active` status.

### 5. `voice_recorder.py` (The Ear)
- Captures system audio input.
- Saves recordings as temporary `.wav` files for processing by the AI handler.

## 🔄 App Workflow

1.  **Input**: The user clicks the microphone button (Start -> Stop recording).
2.  **Audio Processing**: `voice_recorder.py` saves the clip to a temp file.
3.  **AI Transcription**: `ai_handler.py` sends the audio to OpenAI Whisper API.
4.  **AI Parsing**: The resulting text is sent to GPT-4o-mini to extract reminder metadata.
5.  **Persistence**: The structured reminder is saved to `reminders.db`.
6.  **Scheduling**: `scheduler_handler.py` creates a background job for the reminder.
7.  **Trigger**: At the scheduled time, the app plays an `alert.wav` (if present), shows a system notification, and displays a popup.