# Reminder AI Pro

A multiplatform reminder application powered by Python and AI.

## Features
- **One-time Reminders:** Set for specific dates/times or "X minutes ahead".
- **Recurring Reminders:** Every hour, daily, weekly, or monthly.
- **Voice Entry:** Record your voice, transcribed via Whisper and parsed by GPT into structured reminders.
- **Cross-Platform:** Works on Windows, macOS, and Linux.
- **Native Notifications:** Popups, sounds, and system notifications.

## Installation
1. Install dependencies:
   ```bash
   uv sync
   ```

## Running the App
To start the application, use:
```bash
uv run main.py
```

2. Set your OpenAI API Key in the app settings (⚙️ icon) or create a `.env` file:
   ```env
   OPENAI_API_KEY=your_key_here
   ```

## Usage
- Click **"🎤 Voice Reminder"** to start recording. Click again to stop. The AI will process your request. Request examples:
   - "Remind me to call John in 5 minutes"
   - "Remind me to take my medicine, starting tomorrow at 8am and repeat the same day of the week"
   - "Create a reminder to start at noon and repeat every 10 minutes to call to john"
   - "Remind me every 2 hours to walk the dog"
   - "Starting tomorrow at 8am remind me every day to take my medicine"

- Click **"➕ Manual Add"** for quick manual entry (Format: `Text | YYYY-MM-DD HH:MM`).
- Reminders are stored locally in `reminders.db`.

## Note on Sounds
Place an `alert.wav` in the root directory to customize the reminder sound alert.