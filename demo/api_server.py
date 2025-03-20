from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import io
import re
import time
import base64
import os.path

from PIL import Image
from datetime import datetime
from email.message import EmailMessage



# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

date_pattern = r"(\d{2}):(\d{2}):(\d{2})"

def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("demo/token.json"):
        creds = Credentials.from_authorized_user_file("demo/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "demo/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("demo/token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds
    
def get_images_from_gmail(message_id: str, images_id: list[str]) -> list[Image.Image]:

    creds = get_creds()

    try:

        service = build("gmail", "v1", credentials=creds)
        images = []

        for img in images_id:
            attachements = service.users().messages().attachments().get(userId="me", messageId=message_id, id=img).execute()
            data = attachements["data"]
            data = data.replace("-", "+")
            data = data.replace("_", "/")

            image_bytes = base64.b64decode(data)

            image = Image.open(io.BytesIO(image_bytes))

            if image.size[0] > image.size[1]:
                image = image.rotate(180+90, expand=True)

            images.append(image)

        return images


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

def gmail_send_message(imgs: list[Image.Image], text_content: str= "", key_word: str="Swapp"):
    
    creds = get_creds()

    try:
        
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content(text_content)

        message["To"] = "cordharmonie35@gmail.com"
        message["From"] = "cordharmonie35@gmail.com"
        message["Subject"] = key_word

        # attachement
        for i, img in enumerate(imgs):
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            attachment_data = img_bytes.getvalue()

            message.add_attachment(attachment_data, "image", "jpg", filename=f"image_{i+1}.jpg")
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message

def listen_gmail(key_word: str, ref_date: datetime, max_results: int = 5, blacklist_ids: list[str]=[]):
    creds = get_creds()

    buff_ids = None
    trigger = False
    service = build("gmail", "v1", credentials=creds)


    while not trigger:

        try:
            results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=max_results).execute()
            results = results.get("messages", [])
            ids = [result["id"] for result in results if result["id"] not in blacklist_ids]
            print(f">> get last email : {ids}")

            if ids==buff_ids:
                time.sleep(1) # Wait 1 seconde
                continue
            else:
                buff_ids = ids

            for id in ids:

                message = service.users().messages().get(userId="me", id=id).execute()
                payload = message["payload"]
                headers = payload["headers"]
                subject: str = [header["value"] for header in headers if header["name"] == "Subject"][0]
                if subject.startswith(key_word):
                    date_str = [header["value"] for header in headers if header["name"] == "Date"][0]
                    if match_ := re.search(date_pattern, date_str):
                        hour = match_.group(1)
                        minute = match_.group(2)
                        second = match_.group(3)
                    date = datetime(ref_date.year, ref_date.month, ref_date.day, int(hour), int(minute), int(second))
                    if date > ref_date:
                        message_id = message["id"]
                        parts = payload["parts"]
                        images_id = [part["body"]["attachmentId"] for part in parts if part["mimeType"].startswith("image")]
                        trigger = True
                        ref_date = date # Get ONLY the last email with this keyword
            
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    return message_id, images_id

