# YouTube Broadcast Scheduler
Aims to automatically create planned YouTube broadcasts.
Currently in development.

## Installation
You need the following python packages:
- `bs4`
- `google-api-python-client`
- `goolge-auth-oauthlib`
- `google-auth-httplib2`
- `oauth2client`

## Setup
You need to enable the following APIs:
- [Gmail](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
- [Google-Drive](https://console.developers.google.com/apis/api/drive.googleapis.com/overview)
- [YouTube](https://console.cloud.google.com/apis/library/youtube.googleapis.com)

## (planned) Features
- Thumbnail-Upload
- send confirmation and errors over e-mail
- create broadcasts by a schedule
- create broadcasts by mail-information --> optional thumbnail as attachment