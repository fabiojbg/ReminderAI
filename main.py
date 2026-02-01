import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import Database
from ai_handler import AIHandler
from voice_recorder import VoiceRecorder
from scheduler_handler import SchedulerHandler
from datetime import datetime, timedelta
import threading
import os
import json
from dotenv import load_dotenv
from plyer import notification
import pygame

load_dotenv()
pygame.mixer.init()

class ReminderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Reminder AI Pro")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        
        # Initialize Core Modules
        self.db = Database()
        self.ai = AIHandler(os.getenv("OPENAI_API_KEY"))
        self.recorder = VoiceRecorder()
        self.scheduler = SchedulerHandler(self.on_reminder_trigger)

        # UI State
        self.is_recording = False

        # Setup Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        
        # Load existing reminders into scheduler
        self.load_reminders()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Reminders", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        self.voice_btn = ctk.CTkButton(self.sidebar, text="🎤 Voice Reminder", command=self.toggle_voice_recording)
        self.voice_btn.pack(pady=10, padx=20)

        self.manual_btn = ctk.CTkButton(self.sidebar, text="➕ Manual Add", command=self.show_manual_add)
        self.manual_btn.pack(pady=10, padx=20)

        self.settings_btn = ctk.CTkButton(self.sidebar, text="⚙️ Settings", command=self.show_settings)
        self.settings_btn.pack(side="bottom", pady=20, padx=20)

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.list_label = ctk.CTkLabel(self.main_frame, text="Active Reminders", font=ctk.CTkFont(size=16))
        self.list_label.pack(pady=10)

        self.reminder_list = ctk.CTkScrollableFrame(self.main_frame)
        self.reminder_list.pack(fill="both", expand=True)
        
        self.refresh_reminder_list()

    def refresh_reminder_list(self):
        for widget in self.reminder_list.winfo_children():
            widget.destroy()

        reminders = self.db.get_all_active_reminders()
        for r in reminders:
            frame = ctk.CTkFrame(self.reminder_list)
            frame.pack(fill="x", pady=5, padx=5)
            
            trigger_info = r['trigger_time'] if r['trigger_time'] else ""
            if r['recurring_params']:
                params = json.loads(r['recurring_params'])
                recursive_type = params.get('type', '')
                interval = params.get('interval', 1)
                
                if recursive_type == 'minutely':
                    trigger_info = f"every {interval} min"
                elif recursive_type == 'hourly':
                    trigger_info = f"every {interval} hours"
                elif recursive_type == 'daily':
                    trigger_info = f"every {interval} days"
                elif recursive_type == 'weekly':
                    trigger_info = f"every week"
                elif recursive_type == 'monthly':
                    trigger_info = f"every month"
                
                if params.get('start_time'):
                    start_t = datetime.fromisoformat(params['start_time']).strftime("%H:%M")
                    trigger_info += f" (starts {start_t})"

            label_text = f"[{r['trigger_type'].upper()}] {r['text']} - {trigger_info}"
            ctk.CTkLabel(frame, text=label_text).pack(side="left", padx=10)
            
            del_btn = ctk.CTkButton(frame, text="🗑️", width=30, command=lambda rid=r['id']: self.delete_reminder(rid))
            del_btn.pack(side="right", padx=10)

    def load_reminders(self):
        reminders = self.db.get_all_active_reminders()
        for r in reminders:
            self.scheduler.add_reminder_job(r)

    def delete_reminder(self, rid):
        self.db.delete_reminder(rid)
        self.scheduler.remove_reminder_job(rid)
        self.refresh_reminder_list()

    def toggle_voice_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.voice_btn.configure(text="🛑 Stop Recording", fg_color="red")
            self.recorder.start_recording()
        else:
            self.is_recording = False
            self.voice_btn.configure(text="🎤 Voice Reminder", fg_color=["#3B8ED0", "#1F6AA5"])
            path = self.recorder.stop_recording()
            if path:
                threading.Thread(target=self.process_voice, args=(path,), daemon=True).start()

    def process_voice(self, path):
        try:
            text = self.ai.transcribe_audio(path)
            reminder_data = self.ai.parse_reminder(text)
            
            rid = self.db.add_reminder(
                reminder_data['text'],
                reminder_data['trigger_type'],
                reminder_data['trigger_time'],
                reminder_data['recurring_params']
            )
            
            reminder = self.db.get_reminder(rid)
            self.scheduler.add_reminder_job(reminder)
            
            self.after(0, self.refresh_reminder_list)
            self.after(0, lambda: messagebox.showinfo("Success", f"Reminder set: {reminder_data['text']}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.recorder.delete_temp_file(path)

    def show_manual_add(self):
        # Simplistic manual add for now
        dialog = ctk.CTkInputDialog(text="Enter reminder text and time (Format: text | 2026-02-01 15:00):", title="Manual Add")
        input_str = dialog.get_input()
        if input_str and "|" in input_str:
            text, time_str = input_str.split("|")
            rid = self.db.add_reminder(text.strip(), "one-time", time_str.strip())
            reminder = self.db.get_reminder(rid)
            self.scheduler.add_reminder_job(reminder)
            self.refresh_reminder_list()

    def show_settings(self):
        api_key = tk.simpledialog.askstring("Settings", "Enter OpenAI API Key:", show='*')
        if api_key:
            self.ai.set_api_key(api_key)
            # Optionally save to .env or config file
            with open(".env", "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}")

    def on_reminder_trigger(self, reminder):
        print(f"TRIGGERED: {reminder['text']}")
        self.after(0, lambda: self.play_alert_sound())
        self.after(0, lambda: self.send_notification(reminder))
        self.after(0, lambda: self.show_alert_popup(reminder))

    def play_alert_sound(self):
        try:
            # If a custom alert.wav exists, play it. Otherwise, generate a beep.
            if os.path.exists("alert.wav"):
                pygame.mixer.music.load("alert.wav")
                pygame.mixer.music.play()
            else:
                # Fallback to system beep if possible, or just skip
                pass
        except Exception as e:
            print(f"Error playing sound: {e}")

    def send_notification(self, reminder):
        try:
            notification.notify(
                title="Reminder Triggered!",
                message=reminder['text'],
                app_name="Reminder AI Pro",
                timeout=10
            )
        except Exception as e:
            print(f"Error sending notification: {e}")

    def show_alert_popup(self, reminder):
        popup = ctk.CTkToplevel(self)
        popup.title("REMINDER!")
        popup.geometry("300x200")
        popup.attributes("-topmost", True)
        
        label = ctk.CTkLabel(popup, text=reminder['text'], font=ctk.CTkFont(size=14, weight="bold"), wraplength=250)
        label.pack(pady=30, padx=20)
        
        close_btn = ctk.CTkButton(popup, text="Dismiss", command=popup.destroy)
        close_btn.pack(pady=10)

if __name__ == "__main__":
    app = ReminderApp()
    app.mainloop()