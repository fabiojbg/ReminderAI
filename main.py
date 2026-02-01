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

class ReminderDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Add Reminder", reminder_data=None):
        super().__init__(parent)
        self.title(title)
        
        # Center the dialog on screen
        width, height = 500, 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.transient(parent)
        self.grab_set()

        self.result = None
        self.reminder_data = reminder_data

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Reminder Text
        ctk.CTkLabel(self.scroll_frame, text="Reminder Text:").grid(row=0, column=0, sticky="w", pady=(10, 0))
        self.text_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Enter reminder...")
        self.text_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Trigger Type
        ctk.CTkLabel(self.scroll_frame, text="Type:").grid(row=2, column=0, sticky="w")
        self.type_var = ctk.StringVar(value="one-time")
        self.type_seg = ctk.CTkSegmentedButton(self.scroll_frame, values=["one-time", "recurring"], 
                                               variable=self.type_var, command=self.toggle_type_frames)
        self.type_seg.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # One-time Frame
        self.one_time_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.one_time_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.one_time_frame, text="Date (YYYY-MM-DD HH:MM):").grid(row=0, column=0, sticky="w")
        self.date_entry = ctk.CTkEntry(self.one_time_frame, placeholder_text="e.g. 2026-02-01 15:00")
        self.date_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Recurring Frame
        self.recurring_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.recurring_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.recurring_frame, text="Recurrence:").grid(row=0, column=0, sticky="w")
        self.rec_type_var = ctk.StringVar(value="daily")
        self.rec_type_menu = ctk.CTkOptionMenu(self.recurring_frame, 
                                               values=["minutely", "hourly", "daily", "weekly", "monthly"],
                                               variable=self.rec_type_var, command=self.toggle_recurring_fields)
        self.rec_type_menu.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Interval
        self.interval_label = ctk.CTkLabel(self.recurring_frame, text="Interval:")
        self.interval_label.grid(row=2, column=0, sticky="w")
        self.interval_entry = ctk.CTkEntry(self.recurring_frame, placeholder_text="1")
        self.interval_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.interval_entry.insert(0, "1")

        # Specific Time (HH:MM)
        self.time_label = ctk.CTkLabel(self.recurring_frame, text="Time (HH:MM):")
        self.time_label.grid(row=4, column=0, sticky="w")
        self.time_entry = ctk.CTkEntry(self.recurring_frame, placeholder_text="08:00")
        self.time_entry.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        # Day of Week (for Weekly)
        self.day_week_label = ctk.CTkLabel(self.recurring_frame, text="Day of Week:")
        self.day_week_var = ctk.StringVar(value="Monday")
        self.day_week_menu = ctk.CTkOptionMenu(self.recurring_frame, 
                                               values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                               variable=self.day_week_var)

        # Day of Month (for Monthly)
        self.day_month_label = ctk.CTkLabel(self.recurring_frame, text="Day of Month (1-31):")
        self.day_month_entry = ctk.CTkEntry(self.recurring_frame, placeholder_text="1")

        # Start Time (Optional)
        ctk.CTkLabel(self.recurring_frame, text="Start From (Optional - YYYY-MM-DD HH:MM):").grid(row=10, column=0, sticky="w")
        self.start_date_entry = ctk.CTkEntry(self.recurring_frame, placeholder_text="e.g. 2026-02-01 12:00")
        self.start_date_entry.grid(row=11, column=0, sticky="ew", pady=(0, 10))

        # Action Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.save_btn = ctk.CTkButton(button_frame, text="Save", command=self.on_save)
        self.save_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        self.cancel_btn = ctk.CTkButton(button_frame, text="Cancel", fg_color="gray", command=self.destroy)
        self.cancel_btn.pack(side="right", padx=5, expand=True, fill="x")

        # Initial visibility
        self.toggle_type_frames(self.type_var.get())
        if self.reminder_data:
            self.load_data()
        else:
            # Pre-fill date and time 5 minutes ahead for a smoother experience
            # Rounded to the nearest minute
            now = (datetime.now() + timedelta(minutes=5)).replace(second=0, microsecond=0)
            current_full = now.strftime("%Y-%m-%d %H:%M")
            current_time = now.strftime("%H:%M")
            
            # One-time date/time
            self.date_entry.insert(0, current_full)
            
            # Recurring defaults
            self.time_entry.insert(0, current_time)
            self.start_date_entry.insert(0, current_full)

    def toggle_type_frames(self, val):
        if val == "one-time":
            self.one_time_frame.grid(row=4, column=0, sticky="ew")
            self.recurring_frame.grid_forget()
        else:
            self.recurring_frame.grid(row=4, column=0, sticky="ew")
            self.one_time_frame.grid_forget()
            self.toggle_recurring_fields(self.rec_type_var.get())

    def toggle_recurring_fields(self, val):
        self.day_week_label.grid_forget()
        self.day_week_menu.grid_forget()
        self.day_month_label.grid_forget()
        self.day_month_entry.grid_forget()
        self.time_label.grid(row=4, column=0, sticky="w")
        self.time_entry.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        self.interval_label.grid(row=2, column=0, sticky="w")
        self.interval_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        if val == "minutely" or val == "hourly":
            self.time_label.grid_forget()
            self.time_entry.grid_forget()
        elif val == "weekly":
            self.day_week_label.grid(row=6, column=0, sticky="w")
            self.day_week_menu.grid(row=7, column=0, sticky="ew", pady=(0, 10))
            self.interval_label.grid_forget()
            self.interval_entry.grid_forget()
        elif val == "monthly":
            self.day_month_label.grid(row=6, column=0, sticky="w")
            self.day_month_entry.grid(row=7, column=0, sticky="ew", pady=(0, 10))
            self.interval_label.grid_forget()
            self.interval_entry.grid_forget()
        elif val == "daily":
            self.interval_label.grid(row=2, column=0, sticky="w")
            self.interval_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

    def load_data(self):
        self.text_entry.insert(0, self.reminder_data.get('text', ''))
        self.type_var.set(self.reminder_data.get('trigger_type', 'one-time'))
        self.type_seg.set(self.type_var.get())
        
        if self.type_var.get() == 'one-time':
            # ISO to readable format
            try:
                dt = datetime.fromisoformat(self.reminder_data['trigger_time'])
                self.date_entry.insert(0, dt.strftime("%Y-%m-%d %H:%M"))
            except:
                self.date_entry.insert(0, self.reminder_data['trigger_time'])
        else:
            params = json.loads(self.reminder_data['recurring_params'])
            self.rec_type_var.set(params.get('type', 'daily'))
            self.rec_type_menu.set(self.rec_type_var.get())
            self.interval_entry.delete(0, 'end')
            self.interval_entry.insert(0, str(params.get('interval', 1)))
            self.time_entry.insert(0, self.reminder_data.get('trigger_time', ''))
            
            if params.get('day_of_week'):
                self.day_week_var.set(params['day_of_week'])
                self.day_week_menu.set(params['day_of_week'])
            if params.get('day_of_month'):
                self.day_month_entry.insert(0, str(params['day_of_month']))
            if params.get('start_time'):
                try:
                    dt = datetime.fromisoformat(params['start_time'])
                    self.start_date_entry.insert(0, dt.strftime("%Y-%m-%d %H:%M"))
                except:
                    self.start_date_entry.insert(0, params['start_time'])
                    
        self.toggle_type_frames(self.type_var.get())

    def on_save(self):
        text = self.text_entry.get().strip()
        if not text:
            messagebox.showerror("Error", "Reminder text is required")
            return

        trigger_type = self.type_var.get()
        trigger_time = ""
        recurring_params = None

        try:
            if trigger_type == "one-time":
                # Validate date format
                dt_str = self.date_entry.get().strip()
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                trigger_time = dt.isoformat()
            else:
                rec_type = self.rec_type_var.get()
                interval = int(self.interval_entry.get().strip() or 1)
                trigger_time = self.time_entry.get().strip()
                
                recurring_params = {
                    "type": rec_type,
                    "interval": interval
                }
                
                start_dt_str = self.start_date_entry.get().strip()
                if start_dt_str:
                    start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M")
                    recurring_params["start_time"] = start_dt.isoformat()

                if rec_type == "weekly":
                    recurring_params["day_of_week"] = self.day_week_var.get()
                elif rec_type == "monthly":
                    day_m = self.day_month_entry.get().strip()
                    if not day_m: raise ValueError("Day of month required")
                    recurring_params["day_of_month"] = int(day_m)
                
                # Validation for HH:MM for certain types
                if rec_type in ["daily", "weekly", "monthly"]:
                    datetime.strptime(trigger_time, "%H:%M")
                    
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
            return

        self.result = {
            "text": text,
            "trigger_type": trigger_type,
            "trigger_time": trigger_time,
            "recurring_params": recurring_params
        }
        self.destroy()

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
                    trigger_info = f"every day at {r['trigger_time']}" if interval == 1 else f"every {interval} days at {r['trigger_time']}"
                elif recursive_type == 'weekly':
                    trigger_info = f"every {params.get('day_of_week')} at {r['trigger_time']}"
                elif recursive_type == 'monthly':
                    trigger_info = f"every {params.get('day_of_month')}th at {r['trigger_time']}"
                
                if params.get('start_time'):
                    try:
                        start_dt = datetime.fromisoformat(params['start_time'])
                        trigger_info += f" (starting {start_dt.strftime('%Y-%m-%d')})"
                    except: pass
            else:
                try:
                    dt = datetime.fromisoformat(trigger_info)
                    trigger_info = dt.strftime("%Y-%m-%d %H:%M")
                except: pass

            label_text = f"{r['text']}\n({trigger_info})"
            ctk.CTkLabel(frame, text=label_text, justify="left", wraplength=400).pack(side="left", padx=10, pady=5)
            
            # Action Buttons Frame
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=10)

            edit_btn = ctk.CTkButton(btn_frame, text="✏️", width=30, command=lambda rid=r['id']: self.edit_reminder(rid))
            edit_btn.pack(side="left", padx=2)

            del_btn = ctk.CTkButton(btn_frame, text="🗑️", width=30, fg_color="transparent", hover_color="#FF4444", 
                                    text_color="white", command=lambda rid=r['id']: self.delete_reminder(rid))
            del_btn.pack(side="left", padx=2)

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
        dialog = ReminderDialog(self, title="Add Reminder")
        self.wait_window(dialog)
        if dialog.result:
            res = dialog.result
            rid = self.db.add_reminder(res['text'], res['trigger_type'], res['trigger_time'], res['recurring_params'])
            reminder = self.db.get_reminder(rid)
            self.scheduler.add_reminder_job(reminder)
            self.refresh_reminder_list()

    def edit_reminder(self, rid):
        reminder = self.db.get_reminder(rid)
        dialog = ReminderDialog(self, title="Edit Reminder", reminder_data=reminder)
        self.wait_window(dialog)
        if dialog.result:
            res = dialog.result
            self.db.update_reminder(rid, res['text'], res['trigger_type'], res['trigger_time'], res['recurring_params'])
            updated_reminder = self.db.get_reminder(rid)
            # This will replace the existing job thanks to job_id being computed from the database ID
            self.scheduler.add_reminder_job(updated_reminder)
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
        
        # Center the popup on screen
        width, height = 300, 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        popup.attributes("-topmost", True)
        
        label = ctk.CTkLabel(popup, text=reminder['text'], font=ctk.CTkFont(size=14, weight="bold"), wraplength=250)
        label.pack(pady=30, padx=20)
        
        close_btn = ctk.CTkButton(popup, text="Dismiss", command=popup.destroy)
        close_btn.pack(pady=10)

if __name__ == "__main__":
    app = ReminderApp()
    app.mainloop()