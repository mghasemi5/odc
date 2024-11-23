from google_calendar_utils import get_google_calendar_service

def create_clinic_calendars():
    service = get_google_calendar_service()
    calendar_names = ['Timesharing', 'Devicesharing', 'Appointments']

    for name in calendar_names:
        calendar = {
            'summary': name,
            'timeZone': 'America/Los_Angeles',  # Replace with your clinic's timezone
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        print(f"Created calendar: {created_calendar['id']}")
create_clinic_calendars()