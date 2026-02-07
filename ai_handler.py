import os
import json
from openai import OpenAI
from datetime import datetime

class AIHandler:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key) if api_key else None

    def set_api_key(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_file_path):
        if not self.client:
            raise ValueError("API Key not set")
        
        with open(audio_file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                # Whisper is proficient in PT and EN by default
            )
        print(f"--- Transcription result: {transcript.text}")
        return transcript.text

    def parse_reminder(self, text):
        if not self.client:
            raise ValueError("API Key not set")

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = datetime.now().strftime("%A")

        system_prompt = f"""
        You are a helpful assistant that parses natural language into a structured JSON for a reminder app.
        Current time: {current_time} ({day_of_week}). Format here is YYYY-MM-DD HH:MM:SS. 
        Pay special attention to the current day and day of week to calculate requests like "tomorrow", "next Monday", etc.

        The JSON must follow this structure:
        {{
            "text": "The reminder content",
            "trigger_type": "one-time" or "recurring",
            "trigger_time": "ISO 8601 datetime for one-time OR HH:MM for recurring",
            "recurring_params": {{
                "type": "minutely", "hourly", "daily", "weekly", or "monthly",
                "interval": 1, (default is 1, e.g., 'every 10 minutes' -> interval: 10)
                "start_time": "ISO 8601 datetime (optional, specify if a future start time is mentioned)",
                "days_of_week": ["Monday", "Tuesday"...] (only if weekly, ALWAYS a list, even for 1 day),
                "day_of_month": 1...31 (only if monthly)
            }} (null if one-time)
        }}

        Examples:
        - "Remind me to drink water in 10 minutes": {{"text": "Drink water", "trigger_type": "one-time", "trigger_time": "2026-02-01T12:10:00", "recurring_params": null}}
        - "Lembrar de tomar remédio todo dia às 8 da manhã": {{"text": "Tomar remédio", "trigger_type": "recurring", "trigger_time": "08:00", "recurring_params": {{"type": "daily", "interval": 1}}}}
        - "Every 15 minutes call the manager": {{"text": "Call the manager", "trigger_type": "recurring", "trigger_time": null, "recurring_params": {{"type": "minutely", "interval": 15}}}}
        - "Create a reminder to start at noon and repeat every 10 minutes to call John": {{"text": "Call John", "trigger_type": "recurring", "trigger_time": "12:00", "recurring_params": {{"type": "minutely", "interval": 10, "start_time": "2026-02-01T12:00:00"}}}}
        - "Every Monday at 9am tell me to start the report": {{"text": "Start the report", "trigger_type": "recurring", "trigger_time": "09:00", "recurring_params": {{"type": "weekly", "interval": 1, "days_of_week": ["Monday"]}}}}
        - "Schedule a meeting every Monday and Friday at 15:00": {{"text": "Meeting", "trigger_type": "recurring", "trigger_time": "15:00", "recurring_params": {{"type": "weekly", "interval": 1, "days_of_week": ["Monday", "Friday"]}}}}
        - "Remind me at 3 PM today to call mom": {{"text": "Call mom", "trigger_type": "one-time", "trigger_time": "2026-02-01T15:00:00", "recurring_params": null}}

        Return ONLY the JSON.
        """

        response = self.client.chat.completions.create(
            model="gpt-5-nano",
            reasoning_effort="low",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        #print(f"--- Prompt: {system_prompt}")
        parsed_json = json.loads(response.choices[0].message.content)
        print(f"--- AI Parsed JSON: {json.dumps(parsed_json, indent=2)}")
        return parsed_json
