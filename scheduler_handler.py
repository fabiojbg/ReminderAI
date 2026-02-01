from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import json

class SchedulerHandler:
    def __init__(self, trigger_callback):
        self.scheduler = BackgroundScheduler()
        self.trigger_callback = trigger_callback
        self.scheduler.start()

    def add_reminder_job(self, reminder):
        reminder_id = reminder['id']
        text = reminder['text']
        trigger_type = reminder['trigger_type']
        trigger_time = reminder['trigger_time']
        recurring_params = json.loads(reminder['recurring_params']) if reminder['recurring_params'] else None

        job_id = f"reminder_{reminder_id}"

        if trigger_type == 'one-time':
            try:
                run_date = datetime.fromisoformat(trigger_time)
                if run_date > datetime.now():
                    self.scheduler.add_job(
                        self.trigger_callback,
                        trigger=DateTrigger(run_date=run_date),
                        args=[reminder],
                        id=job_id,
                        replace_existing=True
                    )
            except (ValueError, TypeError):
                print(f"Invalid date format for reminder {reminder_id}")

        elif trigger_type == 'recurring':
            interval = recurring_params.get('interval', 1)
            start_date = None
            if recurring_params.get('start_time'):
                try:
                    start_date = datetime.fromisoformat(recurring_params['start_time'])
                except (ValueError, TypeError):
                    pass

            if recurring_params['type'] == 'minutely':
                self.scheduler.add_job(
                    self.trigger_callback,
                    trigger=IntervalTrigger(minutes=interval, start_date=start_date),
                    args=[reminder],
                    id=job_id,
                    replace_existing=True
                )
            elif recurring_params['type'] == 'hourly':
                self.scheduler.add_job(
                    self.trigger_callback,
                    trigger=IntervalTrigger(hours=interval, start_date=start_date),
                    args=[reminder],
                    id=job_id,
                    replace_existing=True
                )
            elif recurring_params['type'] == 'daily':
                hour, minute = trigger_time.split(':')
                self.scheduler.add_job(
                    self.trigger_callback,
                    trigger=CronTrigger(hour=hour, minute=minute, start_date=start_date),
                    args=[reminder],
                    id=job_id,
                    replace_existing=True
                )
            elif recurring_params['type'] == 'weekly':
                hour, minute = trigger_time.split(':')
                day_of_week = recurring_params['day_of_week'].lower()[:3] # 'mon', 'tue', etc.
                self.scheduler.add_job(
                    self.trigger_callback,
                    trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute, start_date=start_date),
                    args=[reminder],
                    id=job_id,
                    replace_existing=True
                )
            elif recurring_params['type'] == 'monthly':
                hour, minute = trigger_time.split(':')
                day = recurring_params['day_of_month']
                self.scheduler.add_job(
                    self.trigger_callback,
                    trigger=CronTrigger(day=day, hour=hour, minute=minute, start_date=start_date),
                    args=[reminder],
                    id=job_id,
                    replace_existing=True
                )

    def remove_reminder_job(self, reminder_id):
        job_id = f"reminder_{reminder_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def shutdown(self):
        self.scheduler.shutdown()