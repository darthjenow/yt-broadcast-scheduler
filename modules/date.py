from datetime import datetime, timezone, timedelta

def add_timezone_offset(date: datetime, hours_offset: int) -> datetime:
	return date.replace(tzinfo=timezone(timedelta(hours=hours_offset), name="TZ"))

def get_iso_date(date: datetime) -> str:
	return date.isoformat()

def get_youtube_title_date(date: datetime, format: str) -> str:
	return date.strftime(format)

def get_next_sunday() -> datetime:
	today = add_timezone_offset(datetime.today(), 1)

	today += timedelta(
		days=6 - today.weekday(),
		hours=10 - today.hour,
		minutes=-today.minute,
		seconds=-today.second,
		microseconds=-today.microsecond
	)

	return today
