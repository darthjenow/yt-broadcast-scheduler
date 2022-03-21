from datetime import datetime, timezone, timedelta
from typing import overload

def get_iso_date(date: datetime) -> str:
	return date.isoformat()

def get_youtube_title_date(date: datetime) -> str:
	return date.strftime("%d.%m.%Y")

@overload
def get_next_weekday(date: datetime, weekday: str = "sunday") -> datetime:
	...
def get_next_weekday(date: datetime, weekday: int = 6) -> datetime:
	if isinstance(weekday, str):
		weekday = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(weekday.lower())

	return date + timedelta(
		days=(7 - date.weekday() + weekday) % 7
	)

def add_timezone_offset(date: datetime, hours_offset: int) -> datetime:
	return date.replace(tzinfo=timezone(timedelta(hours=hours_offset), name="TZ"))

# proof of concept code
today = add_timezone_offset(datetime.today(), 1)

next_sunday = get_next_weekday(today, "sunday")

broadcast_timestamp = get_iso_date(next_sunday)
next_sunday_streamtitle = get_youtube_title_date(next_sunday)

print (broadcast_timestamp)
print (next_sunday_streamtitle)