import datetime
import platform
import subprocess
import textwrap
from ..utils.run_applescript import run_applescript, run_applescript_capture


makeDateFunction = """
on makeDate(yr, mon, day, hour, min, sec)
	set theDate to current date
	tell theDate
		set its year to yr
		set its month to mon
		set its day to day
		set its hours to hour
		set its minutes to min
		set its seconds to sec
	end tell
	return theDate
end makeDate
"""

class Calendar:
    def __init__(self, computer):
        self.computer = computer
        # In the future, we might consider a way to use a different calendar app. For now its Calendar
        self.calendar_app = "Calendar"

    def get_events(self, start_date=datetime.date.today(), end_date=None):
        """
        Fetches calendar events for the given date or date range.
        
        Args:
            start_date: Start datetime (defaults to today)
            end_date: End datetime (defaults to tomorrow)
            
        Returns:
            List of tuples containing (event_title, event_start_date) or error message string
        """
        if platform.system() != "Darwin":
            return "This method is only supported on MacOS"
            
        if not end_date:
            # Default to 1 day from start date
            end_date = start_date + datetime.timedelta(days=1)

        # Convert dates to datetime if needed
        if isinstance(start_date, datetime.date):
            start_date = datetime.datetime.combine(start_date, datetime.time.min)
        if isinstance(end_date, datetime.date):
            end_date = datetime.datetime.combine(end_date, datetime.time.max)

        script = f'''
        use AppleScript version "2.4"
        use scripting additions
        use framework "Foundation" 
        use framework "EventKit"

        -- Convert input dates to NSDate
        set startDate to (current application's NSDate's dateWithTimeIntervalSince1970:{int(start_date.timestamp())})
        set endDate to (current application's NSDate's dateWithTimeIntervalSince1970:{int(end_date.timestamp())})''' + '''

        -- create event store and get the OK to access Calendars
        set theEKEventStore to current application's EKEventStore's alloc()'s init()
        theEKEventStore's requestAccessToEntityType:0 completion:(missing value)

        -- check if app has access
        set authorizationStatus to current application's EKEventStore's authorizationStatusForEntityType:0
        if authorizationStatus is not 3 then
            display dialog "Access must be given in System Preferences" & linefeed & "-> Security & Privacy first." buttons {{"OK"}} default button 1
            tell application "System Settings"
                activate
                tell pane id "com.apple.preference.security" to reveal anchor "Privacy"
            end tell
            error number -128
        end if

        -- get all calendars that can store events
        set theCalendars to theEKEventStore's calendarsForEntityType:0

        -- find matching events across all calendars
        set thePred to theEKEventStore's predicateForEventsWithStartDate:startDate endDate:endDate calendars:theCalendars
        set theEvents to (theEKEventStore's eventsMatchingPredicate:thePred)

        -- sort by date
        set theEvents to theEvents's sortedArrayUsingSelector:"compareStartDateWithEvent:"

        -- return event details
        set eventList to {}
        repeat with thisEvent in theEvents
            set eventTitle to thisEvent's title() as string
            set eventStart to thisEvent's startDate() as date
            set eventEnd to thisEvent's endDate() as date
            set eventLocation to thisEvent's location() as string
            if eventLocation is missing value then set eventLocation to "None"
            set eventNotes to thisEvent's notes() as string
            if eventNotes is missing value then set eventNotes to "None"
            
            set eventDetails to eventTitle & "|" & eventStart & "|" & eventEnd & "|" & eventLocation & "|" & eventNotes
            set end of eventList to eventDetails
        end repeat
        
        return eventList
        '''

        # Dedent script
        script = textwrap.dedent(script)

        try:
            stdout, stderr = run_applescript_capture(script)
            
            if stderr:
                if "Not authorized to send Apple events to Calendar" in stderr:
                    return "Calendar access not authorized. Please allow access in System Preferences > Security & Privacy > Automation."
                return stderr

            events = []
            if stdout.strip():
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        # Parse event details
                        title, start, end, location, notes, attendees = line.strip().split('|')
                        start_dt = datetime.datetime.strptime(start.strip(), '%Y-%m-%d %H:%M:%S +0000')
                        end_dt = datetime.datetime.strptime(end.strip(), '%Y-%m-%d %H:%M:%S +0000')
                        
                        event_str = f"Event: {title} | Start Date: {start_dt} | End Date: {end_dt}"
                        if location != "None":
                            event_str += f" | Location: {location}"
                        if notes != "None":
                            event_str += f" | Notes: {notes}"
                        if attendees != "{}":
                            event_str += f" | Attendees: {attendees}"
                        events.append(event_str)
                        
            return "\n".join(events) if events else "No events found for the specified date."

        except subprocess.CalledProcessError as e:
            return f"Error running AppleScript: {e}"

    def create_event(
        self,
        title: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        location: str = "",
        notes: str = "",
        calendar: str = None,
    ) -> str:
        """
        Creates a new calendar event in the default calendar with the given parameters using AppleScript.
        """
        if platform.system() != "Darwin":
            return "This method is only supported on MacOS"

        # Format datetime for AppleScript
        applescript_start_date = start_date.strftime("%B %d, %Y %I:%M:%S %p")
        applescript_end_date = end_date.strftime("%B %d, %Y %I:%M:%S %p")

        # If there is no calendar, lets use the first calendar applescript returns. This should probably be modified in the future
        if calendar is None:
            calendar = self.get_first_calendar()
            if calendar is None:
                return "Can't find a default calendar. Please try again and specify a calendar name."

        script = f"""
        {makeDateFunction}
        set startDate to makeDate({start_date.strftime("%Y, %m, %d, %H, %M, %S")})
        set endDate to makeDate({end_date.strftime("%Y, %m, %d, %H, %M, %S")})
        -- Open and activate calendar first
        tell application "System Events"
            set calendarIsRunning to (name of processes) contains "{self.calendar_app}"
            if calendarIsRunning then
                tell application "{self.calendar_app}" to activate
            else
                tell application "{self.calendar_app}" to launch
                delay 1 -- Wait for the application to open
                tell application "{self.calendar_app}" to activate
            end if
        end tell
        tell application "{self.calendar_app}"
            tell calendar "{calendar}"
                make new event at end with properties {{summary:"{title}", start date:startDate, end date:endDate, location:"{location}", description:"{notes}"}}
            end tell
            -- tell the Calendar app to refresh if it's running, so the new event shows up immediately
            tell application "{self.calendar_app}" to reload calendars
        end tell
        """

        try:
            run_applescript(script)
            return f"""Event created successfully in the "{calendar}" calendar."""
        except subprocess.CalledProcessError as e:
            return str(e)

    def delete_event(
        self, event_title: str, start_date: datetime.datetime, calendar: str = None
    ) -> str:
        if platform.system() != "Darwin":
            return "This method is only supported on MacOS"

        # The applescript requires a title and start date to get the right event
        if event_title is None or start_date is None:
            return "Event title and start date are required"

        # If there is no calendar, lets use the first calendar applescript returns. This should probably be modified in the future
        if calendar is None:
            calendar = self.get_first_calendar()
            if not calendar:
                return "Can't find a default calendar. Please try again and specify a calendar name."

        script = f"""
        {makeDateFunction}
        set eventStartDate to makeDate({start_date.strftime("%Y, %m, %d, %H, %M, %S")})
        -- Open and activate calendar first
        tell application "System Events"
            set calendarIsRunning to (name of processes) contains "{self.calendar_app}"
            if calendarIsRunning then
                tell application "{self.calendar_app}" to activate
            else
                tell application "{self.calendar_app}" to launch
                delay 1 -- Wait for the application to open
                tell application "{self.calendar_app}" to activate
            end if
        end tell
        tell application "{self.calendar_app}"
            -- Specify the name of the calendar where the event is located
            set myCalendar to calendar "{calendar}"
            
            -- Define the exact start date and name of the event to find and delete
            set eventSummary to "{event_title}"
            
            -- Find the event by start date and summary
            set theEvents to (every event of myCalendar where its start date is eventStartDate and its summary is eventSummary)
            
            -- Check if any events were found
            if (count of theEvents) is equal to 0 then
                return "No matching event found to delete."
            else
                -- If the event is found, delete it
                repeat with theEvent in theEvents
                    delete theEvent
                end repeat
                save
                return "Event deleted successfully."
            end if
        end tell
        """

        stderr, stdout = run_applescript_capture(script)
        if stdout:
            return stdout[0].strip()
        elif stderr:
            if "successfully" in stderr:
                return stderr

            return f"""Error deleting event: {stderr}"""
        else:
            return "Unknown error deleting event. Please check event title and date."

    def get_first_calendar(self) -> str:
        # Literally just gets the first calendar name of all the calendars on the system. AppleScript does not provide a way to get the "default" calendar
        script = f"""
            -- Open calendar first
            tell application "System Events"
                set calendarIsRunning to (name of processes) contains "{self.calendar_app}"
                if calendarIsRunning is false then
                    tell application "{self.calendar_app}" to launch
                    delay 1 -- Wait for the application to open
                end if
            end tell
            tell application "{self.calendar_app}"
            -- Get the name of the first calendar
                set firstCalendarName to name of first calendar
            end tell
            return firstCalendarName
            """
        stdout = run_applescript_capture(script)
        if stdout:
            return stdout[0].strip()
        else:
            return None
