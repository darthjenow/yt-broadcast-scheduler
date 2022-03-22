from email.mime.text import MIMEText
from pathlib import Path
import re
import base64
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = [
	"https://www.googleapis.com/auth/gmail.readonly",
	"https://www.googleapis.com/auth/gmail.modify",
	"https://www.googleapis.com/auth/gmail.send"
]

CLIENT_SECRETS_FILE = Path("SECRET.json")
TOKEN_FILE = Path("TOKEN.GMAIL.json")

def get_service():
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if TOKEN_FILE.exists():
		creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
			CLIENT_SECRETS_FILE, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(TOKEN_FILE, 'w') as token:
			token.write(creds.to_json())

	# Call the Gmail API and return it
	service = build('gmail', 'v1', credentials=creds)

	return service

def check_mail():
	# Call the Gmail API
	service = get_service()
	results = service.users().messages().list(userId="me", q="label:broadcast label:unread").execute()
	messages = results.get("messages", [])

	data = []

	for message in messages:
		mail = service.users().messages().get(userId="me", id=message["id"]).execute()

		# Get value of 'payload' from dictionary 'txt'
		payload = mail['payload']
		headers = payload['headers']

		data.append({})

		# Look for Subject and Sender Email in the headers
		for d in headers:
			if d["name"] == "Subject":
				data[-1]["subject"] = d["value"]
			if d["name"] == "From":
				data[-1]["sender"] = d["value"]
			if d["name"] == "Delivered-To":
				data[-1]["recipent"] = d["value"]
				
		# check if the mail was addressed to the correct sub-mail-address
		if re.match(r".+\+broadcast@gmail\.com", data[-1]["recipent"]):
			# The Body of the message is in Encrypted format. So, we have to decode it.
			# Get the data and decode it with base 64 decoder.
			parts = payload.get('parts')[0]
			message_data = parts['body']['data']
			message_data = message_data.replace("-","+").replace("_","/")
			decoded_data = base64.b64decode(message_data)

			# Now, the data obtained is in lxml. So, we will parse 
			# it with BeautifulSoup library
			soup = BeautifulSoup(decoded_data , "lxml")
			data[-1]["body"] = soup.body()[0].getText()

			# mark the message as read
			service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()

	return data

def send_mails(recipents: list[str], subject: str, body: str, sender: str):
	service = get_service()

	message = MIMEText(body)
	message["to"] = ", ".join(recipents)
	message["from"] = sender
	message["subject"] = subject

	raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))

	message_for_send = {
		"raw": raw_message.decode("utf-8")
	}

	try:
		message = service.users().messages().send(userId="me", body=message_for_send).execute()
		print('Message Id: %s' % message['id'])
		return message
	except Exception as e:
		print('An error occurred: %s' % e)
		return None