#!/usr/bin/python
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
TOKEN_FILE = Path("TOKEN.json")

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

	 %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % (Path(__file__) / CLIENT_SECRETS_FILE).absolute()

def get_authenticated_service():
	flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
		scope=YOUTUBE_READ_WRITE_SCOPE,
		message=MISSING_CLIENT_SECRETS_MESSAGE)

	storage = Storage(TOKEN_FILE)
	credentials = storage.get()

	# if the credentials are invalid or non-existent, get new ones
	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage)

	return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

# Create a liveBroadcast resource and set its title, scheduled start time,
# scheduled end time, and privacy status.
def insert_broadcast(youtube, date):
	insert_broadcast_response = youtube.liveBroadcasts().insert(
		part="snippet,status",
		body=dict(
			snippet=dict(
				title="test-title foobar",
		description="foo\nbar",
		thumbnails=dict(
			url="",
			width=1920,
			height=1080
		),
				scheduledStartTime=date
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
def set_thumbnail(youtube, id, file):
	request = youtube.thumbnails().set(
			videoId=id,
			media_body=MediaFileUpload(file)
	)
	response = request.execute()

	return response

def schedule_broadcast(date, thumbnail):
	youtube = get_authenticated_service()
	try:
		broadcast_id = insert_broadcast(youtube, date)
		
		response = set_thumbnail(youtube, broadcast_id, thumbnail)
		
		print (response)
	except HttpError as e:
		print (f"A HTTP error {e.resp.status} occured:\n{e.content}")
		
		# send mail	

if __name__ == "__main__":
	schedule_broadcast("2022-03-22T00:00:00+01:00", THUMB_FILE)