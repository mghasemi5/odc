

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define the scopes for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
os.environ['GOOGLE_API_CREDENTIALS'] = r'client_secret.json'
def get_google_calendar_service():
    """Authenticate and return a Google Calendar service instance."""
    creds = None
    token_file = 'token.json'  # File where tokens are stored

    # Load existing credentials if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Authenticate if no valid credentials are found
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh the access token
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('GOOGLE_API_CREDENTIALS'), SCOPES
            )
            creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')  # Request offline access

        # Save the credentials for future use
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def sync_event_to_google(instance, calendar_id, summary, description, start_time, end_time):
    """Create or update a Google Calendar event."""
    service = get_google_calendar_service()
    print(f"Event ID for update: {instance.event_id}")
    # Prepare event details
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Tehran'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Tehran'},
    }

    if instance.event_id:  # Update the existing event
        try:
            updated_event = service.events().update(
                calendarId=calendar_id, eventId=instance.event_id, body=event
            ).execute()
            print(f"Updated event: {updated_event['id']}")
        except Exception as e:
            print(f"Error updating event: {e}")
    else:  # Create a new event
        try:
            new_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            instance.event_id = new_event['id']  # Save the event ID for future updates
            instance.save()
            print(f"Created event: {new_event['id']}")
        except Exception as e:
            print(f"Error creating event: {e}")

def delete_event_from_google(instance, calendar_id):
    """Delete a Google Calendar event."""
    if not instance.event_id:
        return  # No event to delete

    service = get_google_calendar_service()
    try:
        service.events().delete(calendarId=calendar_id, eventId=instance.event_id).execute()
        print(f"Deleted event: {instance.event_id}")
    except Exception as e:
        print(f"Error deleting event: {e}")