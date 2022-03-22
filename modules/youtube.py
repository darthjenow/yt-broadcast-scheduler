#!/usr/bin/python
from datetime import datetime
import httplib2
from pathlib import Path

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient.http import MediaFileUpload

THUMB_FILE = Path("thumb.jpg")

CLIENT_SECRETS_FILE = Path("SECRET.json")
TOKEN_FILE = Path("TOKEN.YOUTUBE.json")

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
	flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=SCOPES)

	storage = Storage(TOKEN_FILE)
	credentials = storage.get()

	# if the credentials are invalid or non-existent, get new ones
	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage)

	return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

# Create a liveBroadcast resource and set its title, scheduled start time,
# scheduled end time, and privacy status.
def insert_broadcast(youtube, config: dict):
	insert_broadcast_response = youtube.liveBroadcasts().insert(
		part="snippet,status",
		body=dict(
			snippet=dict(
				title=config["title"],
		description=config["description"],
		thumbnails=dict(
			url="",
			width=1920,
			height=1080
		),
				scheduledStartTime=config["scheduleDate"]
			),
			status=dict(
				privacyStatus="private",
				selfDeclaredMadeForKids=False
			)
		)
	).execute()

	snippet = insert_broadcast_response["snippet"]

	# TOOD: write to log instead
	print ("Broadcast '%s' with title '%s' was published at '%s'." % (insert_broadcast_response["id"], snippet["title"], snippet["publishedAt"]))

	return insert_broadcast_response["id"]

# upload a thumbnail for a broadcast identified by its video-id
def set_thumbnail(youtube, id: str, file: Path):
	request = youtube.thumbnails().set(
			videoId=id,
			media_body=MediaFileUpload(file)
	)
	response = request.execute()

	return response

def schedule_broadcast(thumbnail_path: Path, config: dict):
	youtube = get_authenticated_service()
	try:
		broadcast_id = insert_broadcast(youtube, config)
		
		response = set_thumbnail(youtube, broadcast_id, thumbnail_path)
	except HttpError as e:
			print (f"A HTTP error {e.resp.status} occured:\n{e.content}")