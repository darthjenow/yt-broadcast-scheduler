#!/usr/bin/python
import httplib2
from pathlib import Path
import tempfile

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient.http import MediaFileUpload

from modules import gdrive

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
		part="snippet,status,contentDetails",
		body={
			"snippet": {
				"title": config["title"],
				"description": config["description"],
				"scheduledStartTime": config["scheduleDate"]
			},
			"status": {
				"privacyStatus": config["privacyStatus"],
				"selfDeclaredMadeForKids": False
			},
			"contentDetails": {
				"enableAutoStart": True,
				"enableAutoStop": True
			}
		}
	).execute()

	return insert_broadcast_response

# upload a thumbnail for a broadcast identified by its video-id
def set_thumbnail(youtube, id: str, config):
	# download the thumbnail from youtube
	thumbnail_fo = tempfile.NamedTemporaryFile(delete=False)
	thumbnail_fo.close()

	thumbnail = Path(thumbnail_fo.name)

	gdrive.download_file(config["thumbnailPath"], thumbnail)

	request = youtube.thumbnails().set(
			videoId=id,
			media_body=MediaFileUpload(thumbnail)
	)
	response = request.execute()

	thumbnail.unlink()

	return response

def set_snippets(youtube, id: str, config):
	response = youtube.videos().update(
		part="snippet",
		body={
			"id": id,
			"snippet": {
				"title": config["title"],
				"categoryId": config["category"],
				"description": config["description"],
				"scheduledStartTime": config["scheduleDate"]
			}
		}
	).execute()

	return response	

def add_playlists(youtube, broadcast_id, playlists):
	responses = []

	for playlist in playlists:
		response = youtube.playlistItems().insert(
			part="snippet",
			body={
				"snippet": {
					"playlistId": playlist,
					"resourceId": {
						"kind": "youtube#video",
						"videoId": broadcast_id
					}
				}
			}
		).execute()

		responses.append(response)

	return responses

def schedule_broadcast(thumbnail_path: Path, config: dict):
	youtube = get_authenticated_service()
	try:
		print ("creating the broadcast")
		result = insert_broadcast(youtube, config)

		broadcast_id = result["id"]
		title = result["snippet"]["title"]
		published_at = result["snippet"]["publishedAt"]

		print(f"Broadwast '{broadcast_id}' with title '{title} was published at '{published_at}'")

		print ("\nSetting the snippets")
		print (set_snippets(youtube, broadcast_id, config))

		print (f"\nSetting the thumbnail")
		print (set_thumbnail(youtube, broadcast_id, thumbnail_path))

		print (f"\nAdding to playlists")
		print (add_playlists(youtube, broadcast_id, config["playlists"]))
	except HttpError as e:
			print (f"A HTTP error {e.resp.status} occured:\n{e.content}")