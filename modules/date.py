from datetime import datetime, timezone, timedelta
from typing import overload

def add_timezone_offset(date: datetime, hours_offset: int) -> datetime:
	return date.replace(tzinfo=timezone(timedelta(hours=hours_offset), name="TZ"))

def get_iso_date(date: datetime) -> str:
	return date.isoformat()

def get_youtube_title_date(date: datetime, format: str) -> str:
	return date.strftime(format)

@overload
def get_next_weekday(date: datetime = add_timezone_offset(datetime.today(), 1), weekday: str = "sunday") -> datetime:
	...
def get_next_weekday(date: datetime = add_timezone_offset(datetime.today(), 1), weekday: int = 6) -> datetime:
	if isinstance(weekday, str):
		weekday = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(weekday.lower())

	return date + timedelta(
		days=(7 - date.weekday() + weekday) % 7
	)
