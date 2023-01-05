from datetime import datetime
from datetime import timedelta


class ScheduleDay:
    def __init__(
        self, num: int, days_type: str,
    ):
        self.num = num
        self.days_type = days_type

    def next_date(self):
        today = datetime.now()
        cycle = {"month": 30, "week": 7, "year": 365}
        billing = {"num": self.num, "type": self.days_type}
        schedule_days = int(billing["num"]) * cycle[billing["type"]]
        next_schedule_day = (today + timedelta(days=int(schedule_days))).strftime(
            "%b %d,%Y"
        )
        return next_schedule_day
