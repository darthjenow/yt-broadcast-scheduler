from datetime import datetime
import json
from pathlib import Path
from datetime import datetime
import tempfile

from modules import mail, youtube, date, gdrive

config = {}

def load_config(config_path: Path = Path("config.json")):
	global config
	config = json.loads(config_path.read_text(encoding="utf-8"))

def main():
	load_config()

	# check the mail
	data = mail.check_mail()

	if len(data) > 0:
		for dataset in data:
			print (dataset)

			broadcast_data = config["broadcast"]

			# insert the custom text
			if dataset["body"] == "":
				broadcast_data["description"] = broadcast_data["description"].replace("SPRUCH_ZUM_SONNTAG\n\n", "")
			else:
				broadcast_data["description"] = broadcast_data["description"].replace("SPRUCH_ZUM_SONNTAG\n\n", dataset["body"] + "\n")

			_date = datetime.fromisoformat(dataset["subject"])
			_date = date.add_timezone_offset(_date, 1)

			broadcast_data["title"] = broadcast_data["title"].replace("SONNTAGS_DATUM", _date.strftime(config["date"]["titleFormat"]))
			broadcast_data["description"] = broadcast_data["description"].replace("SONNTAGS_DATUM", _date.strftime(config["date"]["descriptionFormat"]))

			broadcast_data["scheduleDate"] = date.get_iso_date(_date)

			# download the thumbnail from youtube
			thumbnail_fo = tempfile.NamedTemporaryFile(delete=False)
			thumbnail_fo.close()

			thumbnail = Path(thumbnail_fo.name)
			drive_path = Path(config["gDrive"]["path"]) / Path(date.get_youtube_title_date(_date, config["date"]["thumbnailFormat"]))

			gdrive.download_file(drive_path, thumbnail)

			# create the schedule
			youtube.schedule_broadcast(thumbnail, broadcast_data)

			thumbnail.unlink()

if __name__ == "__main__":
	main()