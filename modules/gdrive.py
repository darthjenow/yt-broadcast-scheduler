from pathlib import Path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

SECRETS_FILE = Path("SECRET.json")
TOKEN_FILE = Path("TOKEN.GDRIVE.json")

def get_service(secrets_file: Path = SECRETS_FILE, token_file: Path = TOKEN_FILE):
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if token_file.exists():
		creds = Credentials.from_authorized_user_file(token_file, SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				secrets_file, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with token_file.open('w') as token:
			token.write(creds.to_json())

	service = build("drive", "v3", credentials=creds)

	return service

def get_dir_id(path: Path) -> str:
	if path.parent == Path("."):
		id = "root"
	else:
		id = get_dir_id(path.parent)

	service = get_service()

	results = service.files().list(q=f"'{id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{path.name}'").execute()

	return results["files"][0]["id"]


def get_file_id(path: Path) -> str:
	service = get_service()

	id = get_dir_id(path.parent)

	results = service.files().list(q=f"'{id}' in parents and name='{path.name}'").execute()
	
	if len(results["files"]) > 0:
		return results["files"][0]["id"]
	else:
		return ""

def download_file(path: Path, save_as: Path):
	id = get_file_id(path)

	service = get_service()

	request = service.files().get_media(fileId=id)
	fh = io.BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
		print ("Download %d%%." % int(status.progress() * 100))

	save_as.write_bytes(fh.getbuffer())