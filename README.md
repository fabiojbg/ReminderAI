# Reminder AI Pro

A multiplatform desktop reminder application powered by Python and AI. Reminder AI Pro converts your natural language (voice or text) into structured, actionable reminders using OpenAI Whisper and GPT models.

## 🚀 Features
- **Voice Entry:** Record your voice, transcribed via Whisper and parsed by GPT-4o-mini into structured reminders.
- **One-time Reminders:** Set for specific dates/times or "X minutes ahead".
- **Advanced Recurring Reminders:**
  - **Minutely/Hourly:** Repeat every X minutes or hours.
  - **Daily:** Repeat every X days at a specific time.
  - **Weekly:** Select specific days of the week.
  - **Monthly:** Repeat on a specific day of the month.
- **Missed Reminder Detection:** Automatically detects and highlights reminders that were missed while the application was closed.
- **Native Experience:** System notifications (via `plyer`), sound alerts (via `pygame`), and a modern UI using `CustomTkinter`.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)

### Setup
1. Clone the repository and install dependencies:
   ```bash
   uv sync
   ```

2. Set your OpenAI API Key in the app settings (⚙️ icon) or create a `.env` file (see `.env.sample`).

## 🏃 Running the App
To start the application, use:
```bash
uv run main.py
```

## ⚙️ Configuration (Advanced)
Reminder AI Pro supports highly flexible AI configurations. You can use the primary `OPENAI_API_KEY` or specify individual providers/models in your `.env` file or through the UI settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `CHAT_API_KEY` | API Key to LLM that interprets voice instructios | - |
| `CHAT_MODEL` | Model for parsing reminders | `gpt-4o-mini` |
| `CHAT_BASE_URL` | Custom endpoint for Chat (e.g., OpenRouter, Local LLM) | OpenAI |
| `TRANSCRIPTION_API_KEY` | API Key to LLM that transcribes voice | - |
| `TRANSCRIPTION_MODEL` | Model for voice transcription | `whisper-1` |
| `TRANSCRIPTION_BASE_URL`| Custom endpoint for Voice Transcription | OpenAI |

## 🎤 Usage Examples
Click **"🎤 Voice Reminder"** to start recording. Request examples:
- *"Remind me to call John in 5 minutes"*
- *"Remind me to take my medicine every day at 8am starting tomorrow"*
- *"Every 15 minutes remind me to stretch"*
- *"Schedule a meeting every Monday and Friday at 3 PM"*
- *"Remind me to pay the rent on the 1st of every month at 9am"*

Click **"➕ Manual Add"** for precise control over intervals, start dates, and specific days of the week.

## 🔔 Note on Sounds
The app looks for an `alert.wav` file in the root directory. If present, it will be used as the alarm sound. If not, it defaults to the system bell.

## 💾 Storage
All reminders are stored locally in a SQLite database (`reminders.db`).
