from datetime import datetime, timezone, timedelta

def add_timezone_offset(date: datetime, hours_offset: int) -> datetime:
	return date.replace(tzinfo=timezone(timedelta(hours=hours_offset), name="TZ"))

def add_timezone(date: datetime) -> datetime:
	# create the switching dates in the same year
	march_switch = datetime(date.year, 3, 31)
	march_switch -= timedelta(days=(march_switch.weekday() + 1) % 7)

	october_switch = datetime(date.year, 10, 31)
	october_switch -= timedelta(days=(october_switch.weekday() + 1) % 7)

	if march_switch < date < october_switch:
		date = add_timezone_offset(date, 2)
	else:
		date = add_timezone_offset(date, 1)

	return date

def get_iso_date(date: datetime) -> str:
	return date.isoformat()

def get_youtube_title_date(date: datetime, format: str) -> str:
	return date.strftime(format)

def get_next_sunday() -> datetime:
	today = datetime.today()

	today += timedelta(
		days=6 - today.weekday(),
		hours=10 - today.hour,
		minutes=-today.minute,
		seconds=-today.second,
		microseconds=-today.microsecond
	)

	today = add_timezone(today)

	return today
