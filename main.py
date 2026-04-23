import requests
from dotenv import load_dotenv
import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_tasks():
    vikunja_base_url = os.getenv("VIKUNJA_BASE_URL")
    vikunja_token = os.getenv("VIKUNJA_TOKEN")

    url = f"{vikunja_base_url}/api/v1/tasks"

    querystring = {"filter":"due_date < 2026-04-24 && done = false","sort_by":["priority","due_date"],"order_by":"desc"}

    headers = {"authorization": f"Bearer {vikunja_token}"}

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()

def filter_task_with_valid_duration(tasks):
    filtered = []

    for task in tasks:
        description = task['description']
        match = re.search(r'duration_minutes:\s*(\d+)', description)

        if match:
            filtered.append([task, int(match.group(1))])

    return filtered

def filter_task_with_duration(tasks):
    filtered = [obj for obj in tasks if "duration_minutes" in obj["description"]]
    return filtered

def request_new_token():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

    # Modifica per aprire una sola finestra
    return flow.run_local_server(port=0)

def get_service():
    credentials = None

    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not credentials or not credentials.valid or (credentials.expired and credentials.refresh_token):
        credentials = request_new_token()
        with open("token.json", "w") as token_file:
            token_file.write(credentials.to_json())

    return build("calendar", "v3", credentials=credentials)

def create_sequential_events(tasks):
    service = get_service()
    now = datetime.now(tz=timezone.utc)
    current_start = now
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    for [task, duration] in tasks:
        duration = duration if duration >= 15 else 15  # durata minima di 15 minuti
        current_end = current_start + timedelta(minutes=duration)

        event = {
            "summary": task["title"],
            "start": {"dateTime": current_start.isoformat(), "timeZone": os.getenv("TZ", "UTC")},
            "end":   {"dateTime": current_end.isoformat(),   "timeZone": os.getenv("TZ", "UTC")},
        }

        created = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Creato: {created['summary']} → {created['htmlLink']}")

        current_start = current_end  # il prossimo inizia dove finisce questo

def main():
    load_dotenv()  # carica il file .env nella directory corrente

    tasks = get_tasks()
    filtered_tasks = filter_task_with_duration(tasks)
    filtered_tasks = filter_task_with_valid_duration(filtered_tasks)

    create_sequential_events(filtered_tasks)


if __name__ == "__main__":
    main()
