import json
from pathlib import Path
from datetime import datetime
import tempfile

from modules import youtube, date, gdrive

config = {}

def load_config(config_path: Path = Path("config.json")):
	global config
	config = json.loads(config_path.read_text(encoding="utf-8"))

def main():
	load_config()

	broadcast_data = config["broadcast"]

	next_sunday = date.get_next_sunday()

	broadcast_data["title"] = broadcast_data["title"].replace("SONNTAGS_DATUM", next_sunday.strftime(config["date"]["titleFormat"]))
	broadcast_data["description"] = broadcast_data["description"]	

	# broadcast_data["scheduleDate"] = date.get_iso_date(next_sunday)
	broadcast_data["scheduleDate"] = "2022-03-27T10:00:00+01:00"

	# download the thumbnail from youtube
	thumbnail_fo = tempfile.NamedTemporaryFile(delete=False)
	thumbnail_fo.close()

	thumbnail = Path(thumbnail_fo.name)
	drive_path = Path(config["gDrive"]["path"]) / Path(date.get_youtube_title_date(next_sunday, config["date"]["thumbnailFormat"]))

	gdrive.download_file(drive_path, thumbnail)

	# create the schedule
	youtube.schedule_broadcast(thumbnail, broadcast_data)

	thumbnail.unlink()

if __name__ == "__main__":
	main()