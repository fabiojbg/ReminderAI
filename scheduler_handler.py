from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import json
import calendar

class SchedulerHandler:
    def __init__(self, trigger_callback):
        self.scheduler = BackgroundScheduler()
        self.trigger_callback = trigger_callback
        self.scheduler.start()

    def add_reminder_job(self, reminder):
        try:
            reminder_id = reminder['id']
            trigger_type = reminder['trigger_type']
            trigger_time = reminder['trigger_time']
            recurring_params = json.loads(reminder['recurring_params']) if reminder['recurring_params'] else None

            job_id = f"reminder_{reminder_id}"

            if trigger_type == 'one-time':
                run_date = datetime.fromisoformat(trigger_time)
                if run_date > datetime.now():
                    self.scheduler.add_job(
                        self.trigger_callback,
                        trigger=DateTrigger(run_date=run_date),
                        args=[reminder],
                        id=job_id,
                        replace_existing=True
                    )
                else:
                    print(f"Skipping scheduling for one-time reminder {reminder_id} as it is in the past.")

            elif trigger_type == 'recurring':
                interval = recurring_params.get('interval', 1)
                start_date = None
                if recurring_params.get('start_time'):
                    try:
                        start_date = datetime.fromisoformat(recurring_params['start_time'])
                    except (ValueError, TypeError):
                        pass

                rec_type = recurring_params.get('type')
                if not rec_type:
                    print(f"Missing recurrence type for reminder {reminder_id}")
                    return

                if rec_type == 'minutely':
                    self.scheduler.add_job(
                        self.trigger_callback,
                        trigger=IntervalTrigger(minutes=interval, start_date=start_date),
                        args=[reminder],
                        id=job_id,
                        replace_existing=True
                    )
                elif rec_type == 'hourly':
                    self.scheduler.add_job(
                        self.trigger_callback,
                        trigger=IntervalTrigger(hours=interval, start_date=start_date),
                        args=[reminder],
                        id=job_id,
                        replace_existing=True
                    )
                elif rec_type in ['daily', 'weekly', 'monthly']:
                    if not trigger_time or ':' not in trigger_time:
                        print(f"Invalid trigger_time format '{trigger_time}' for reminder {reminder_id}")
                        return
                        
                    hour, minute = trigger_time.split(':')
                    
                    if rec_type == 'daily':
                        self.scheduler.add_job(
                            self.trigger_callback,
                            trigger=CronTrigger(hour=hour, minute=minute, start_date=start_date),
                            args=[reminder],
                            id=job_id,
                            replace_existing=True
                        )
                    elif rec_type == 'weekly':
                        days = recurring_params.get('days_of_week')
                        if not days:
                            # Fallback for old single day format
                            days = [recurring_params.get('day_of_week')]
                        
                        # Convert to comma separated short names (mon,tue,...)
                        day_of_week = ",".join([d.lower()[:3] for d in days if d])
                        
                        self.scheduler.add_job(
                            self.trigger_callback,
                            trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute, start_date=start_date),
                            args=[reminder],
                            id=job_id,
                            replace_existing=True
                        )
                    elif rec_type == 'monthly':
                        day = recurring_params['day_of_month']
                        self.scheduler.add_job(
                            self.trigger_callback,
                            trigger=CronTrigger(day=day, hour=hour, minute=minute, start_date=start_date),
                            args=[reminder],
                            id=job_id,
                            replace_existing=True
                        )
        except Exception as e:
            print(f"Error scheduling job for reminder {reminder.get('id')}: {e}")

    def remove_reminder_job(self, reminder_id):
        job_id = f"reminder_{reminder_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def shutdown(self):
        self.scheduler.shutdown()

    @staticmethod
    def get_last_theoretical_trigger(reminder):
        """Calculates the last time this reminder should have triggered before now."""
        trigger_type = reminder['trigger_type']
        trigger_time = reminder['trigger_time']
        recurring_params = json.loads(reminder['recurring_params']) if reminder['recurring_params'] else None
        now = datetime.now()

        if trigger_type == 'one-time':
            try:
                dt = datetime.fromisoformat(trigger_time)
                return dt if dt < now else None
            except:
                return None

        elif trigger_type == 'recurring':
            try:
                start_date = None
                if recurring_params.get('start_time'):
                    start_date = datetime.fromisoformat(recurring_params['start_time'])
                
                # If start_date is in the future, it hasn't triggered yet
                if start_date and start_date > now:
                    return None

                rec_type = recurring_params['type']
                interval = recurring_params.get('interval', 1)

                if rec_type == 'minutely':
                    # Simplified: if we have a start_date, calculating intervals from it. 
                    # If not, it's hard to know the 'anchor'. Assume start of current hour as anchor if no start_date.
                    anchor = start_date if start_date else now.replace(minute=0, second=0, microsecond=0)
                    if anchor > now: return None
                    diff_minutes = int((now - anchor).total_seconds() / 60)
                    last_trigger_minutes = (diff_minutes // interval) * interval
                    return anchor + timedelta(minutes=last_trigger_minutes)

                elif rec_type == 'hourly':
                    anchor = start_date if start_date else now.replace(minute=0, second=0, microsecond=0)
                    if anchor > now: return None
                    diff_hours = int((now - anchor).total_seconds() / 3600)
                    last_trigger_hours = (diff_hours // interval) * interval
                    return anchor + timedelta(hours=last_trigger_hours)

                elif rec_type == 'daily':
                    hour, minute = map(int, trigger_time.split(':'))
                    # Today's theoretical trigger
                    theoretical = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    if start_date:
                        # Find how many intervals since start_date
                        days_since = (now.date() - start_date.date()).days
                        relevant_days_since = (days_since // interval) * interval
                        theoretical = start_date.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=relevant_days_since)
                    else:
                        if theoretical > now:
                            theoretical -= timedelta(days=interval)
                    
                    return theoretical if theoretical < now else None

                elif rec_type == 'weekly':
                    hour, minute = map(int, trigger_time.split(':'))
                    days = recurring_params.get('days_of_week')
                    if not days:
                        days = [recurring_params.get('day_of_week')]
                    
                    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    target_weekdays = [weekdays.index(d.lower()) for d in days if d]
                    
                    last_theoretical = None
                    for target_weekday in target_weekdays:
                        days_back = (now.weekday() - target_weekday) % 7
                        theoretical = (now - timedelta(days=days_back)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        if theoretical > now:
                            theoretical -= timedelta(days=7)
                        
                        if last_theoretical is None or theoretical > last_theoretical:
                            last_theoretical = theoretical
                    
                    return last_theoretical

                elif rec_type == 'monthly':
                    hour, minute = map(int, trigger_time.split(':'))
                    day = recurring_params['day_of_month']
                    
                    # Try current month
                    try:
                        theoretical = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                    except ValueError: # Day 31 in a 30-day month
                        # Move to last day of month
                        last_day = calendar.monthrange(now.year, now.month)[1]
                        theoretical = now.replace(day=last_day, hour=hour, minute=minute, second=0, microsecond=0)

                    if theoretical > now:
                        # Go to previous month
                        prev_month = now.month - 1 if now.month > 1 else 12
                        prev_year = now.year if now.month > 1 else now.year - 1
                        last_day_prev = calendar.monthrange(prev_year, prev_month)[1]
                        target_day = min(day, last_day_prev)
                        theoretical = datetime(prev_year, prev_month, target_day, hour, minute)
                    
                    return theoretical

            except Exception as e:
                print(f"Error calculating last trigger: {e}")
                return None
        return None
