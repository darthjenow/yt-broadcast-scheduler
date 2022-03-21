from email.mime.text import MIMEText
from pathlib import Path
import re
import base64
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
	"https://www.googleapis.com/auth/gmail.readonly",
	"https://www.googleapis.com/auth/gmail.modify",
	"https://www.googleapis.com/auth/gmail.send"
]

CLIENT_SECRETS_FILE = Path("SECRET.json")
TOKEN_FILE = Path("TOKEN.GMAIL.json")
SENDER_NAME = "broadcast-logging"

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
	try:
		# Call the Gmail API
		service = get_service()
		results = service.users().messages().list(userId="me", q="label:broadcast label:unread").execute()
		messages = results.get("messages", [])

		if not messages:
			print("No new message found")
			return

		for message in messages:
			mail = service.users().messages().get(userId="me", id=message["id"]).execute()

			# Get value of 'payload' from dictionary 'txt'
			payload = mail['payload']
			headers = payload['headers']

			# Look for Subject and Sender Email in the headers
			for d in headers:
				if d["name"] == "Subject":
					subject = d["value"]
				if d["name"] == "From":
					sender = d["value"]
				if d["name"] == "Delivered-To":
					recipent = d["value"]
					
			# check if the mail was addressed to the correct sub-mail-address
			if re.match(r".+\+broadcast@gmail\.com", recipent):
				# The Body of the message is in Encrypted format. So, we have to decode it.
				# Get the data and decode it with base 64 decoder.
				parts = payload.get('parts')[0]
				data = parts['body']['data']
				data = data.replace("-","+").replace("_","/")
				decoded_data = base64.b64decode(data)
	
				# Now, the data obtained is in lxml. So, we will parse 
				# it with BeautifulSoup library
				soup = BeautifulSoup(decoded_data , "lxml")
				body = soup.body()[0]
	
				# Printing the subject, sender's email and message
				print("Subject: ", subject)
				print("From: ", sender)
				print(f"Recipent: {recipent}")
				print("Message: ", body)

				# mark the message as read
				service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()

	except HttpError as error:
		# TODO(developer) - Handle errors from gmail API.
		print(f'An error occurred: {error}')

def send_mail(recipent, subject, body):
	service = get_service()

	message = MIMEText(body)
	message["to"] = recipent
	message["from"] = SENDER_NAME
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


if __name__ == '__main__':
	# check_mail()
	send_mail("RECIPENT_MAIL_ADDRESS", "foobar0", "text0\ntext1")