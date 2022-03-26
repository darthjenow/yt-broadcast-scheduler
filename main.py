import json
from pathlib import Path

from modules import youtube, date

config = {}

def load_config(config_path: Path = Path("config.json")):
	global config
	config = json.loads(config_path.read_text(encoding="utf-8"))

def main():
	load_config()

	broadcast_data = config["broadcast"]

	next_sunday = date.get_next_sunday()

	broadcast_data["title"] = broadcast_data["title"].replace("SONNTAGS_DATUM", next_sunday.strftime(config["date"]["titleFormat"]))
	broadcast_data["description"] = broadcast_data["description"].replace("SONNTAGS_DATUM", next_sunday.strftime(config["date"]["titleFormat"]))

	broadcast_data["scheduleDate"] = date.get_iso_date(next_sunday)
	broadcast_data["thumbnailPath"] = Path(config["gDrive"]["path"]) / Path(date.get_youtube_title_date(next_sunday, config["date"]["thumbnailFormat"]))

	# create the schedule
	youtube.schedule_broadcast(broadcast_data, broadcast_data)

if __name__ == "__main__":
	main()