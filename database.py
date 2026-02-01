import sqlite3
import json

class Database:
    def __init__(self, db_name="reminders.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    trigger_type TEXT NOT NULL, -- 'one-time' or 'recurring'
                    trigger_time TEXT NOT NULL, -- ISO Format or specific time string
                    recurring_params TEXT,      -- JSON string for recurring options
                    active INTEGER DEFAULT 1
                )
            ''')
            conn.commit()

    def add_reminder(self, text, trigger_type, trigger_time, recurring_params=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders (text, trigger_type, trigger_time, recurring_params)
                VALUES (?, ?, ?, ?)
            ''', (text, trigger_type, trigger_time, json.dumps(recurring_params) if recurring_params else None))
            conn.commit()
            return cursor.lastrowid

    def get_all_active_reminders(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reminders WHERE active = 1')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_reminder(self, reminder_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE reminders SET active = 0 WHERE id = ?', (reminder_id,))
            conn.commit()

    def get_reminder(self, reminder_id):
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reminders WHERE id = ?', (reminder_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_reminder(self, reminder_id, text, trigger_type, trigger_time, recurring_params=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reminders
                SET text = ?, trigger_type = ?, trigger_time = ?, recurring_params = ?
                WHERE id = ?
            ''', (text, trigger_type, trigger_time, json.dumps(recurring_params) if recurring_params else None, reminder_id))
            conn.commit()
