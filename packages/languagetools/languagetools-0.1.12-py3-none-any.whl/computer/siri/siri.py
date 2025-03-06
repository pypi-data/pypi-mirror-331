import subprocess

system_message = """You are an AI that responds with Applescript code to achieve the users goal, enclosed in <applescript>...</applescript> XML tags. First, think about the goal and how to achieve it. Then, write the Applescript code to achieve the goal."""

system_message += """
Some examples of good Applescript:

Finding a calendar matching a specific name
<applescript>
tell application "Calendar"
    set theCalendarName to "Project Calendar"
    set theCalendar to first calendar where its name = theCalendarName
end tell
</applescript>

Creating a new event
<applescript>
set theStartDate to (current date) + (1 * days)
set hours of theStartDate to 15
set minutes of theStartDate to 0
set seconds of theStartDate to 0
set theEndDate to theStartDate + (1 * hours)
 
tell application "Calendar"
    tell calendar "Project Calendar"
        make new event with properties {summary:"Important Meeting!", start date:theStartDate, end date:theEndDate}
    end tell
end tell
</applescript>

Finding an event by UID
<applescript>
tell application "Calendar"
    tell calendar "Project Calendar"
        first event where its uid = "538E181E-7043-45A5-8F61-4711724F1A1B"
    end tell
end tell
</applescript>

Adding alarms to an event
<applescript>
tell application "Calendar"
    tell calendar "Project Calendar"
        set theEvent to (first event where its summary = "Important Meeting!")
        tell theEvent
            -- Add a message alarm
            make new display alarm at end of display alarms with properties {trigger interval:-5}
 
            -- Add a message with sound alarm
            make new sound alarm at end of sound alarms with properties {trigger interval:-5, sound name:"Sosumi"}
        end tell
    end tell
    reload calendars
end tell
</applescript>

Adding an attendee to an event
<applescript>
tell application "Calendar"
    tell calendar "Project Calendar"
        set theEvent to (first event where its summary = "Important Meeting!")
        tell theEvent
            make new attendee at end of attendees with properties {email:"example@apple.com"}
        end tell
    end tell
    reload calendars
end tell
</applescript>
"""

class Siri:
    def __init__(self, computer):
        self.computer = computer

    def query(self, query):
        query = f"I need Applescript that does this: {query}"
        while True:
            print(f"Querying Siri with: {query}")
            applescript_code = self.computer.ai.chat(query, system_message=system_message, model_size="large", display=True)
            print(f"Got AppleScript code: {applescript_code}")
            
            # Extract applescript code from response
            try:
                # Try <applescript> tags first
                if "<applescript>" in applescript_code:
                    applescript_code = applescript_code.split("<applescript>")[1].split("</applescript>")[0]
                # Try markdown code blocks
                elif "```applescript" in applescript_code:
                    applescript_code = applescript_code.split("```applescript")[1].split("```")[0]
                elif "```" in applescript_code:
                    applescript_code = applescript_code.split("```")[1].split("```")[0]
                else:
                    raise IndexError
            except IndexError:
                message = "\n\nYou didn't properly enclose your AppleScript code in <applescript> tags or ``` code blocks. Please try again."
                query = query.replace(message, "")
                query += message
                continue

            # First try compiling
            is_valid, error = self.compile(applescript_code)
            if not is_valid:
                query = query.replace(f"\n\nPlease write new Applescript to help me achieve my goal. First, think for a moment about what went wrong and how to fix it!", "")
                query += f"\n\nI wrote this AppleScript code:\n\n{applescript_code}\n\nBut it failed to compile with error:\n{error}\n\nPlease write new Applescript to help me achieve my goal. First, think for a moment about what went wrong and how to fix it!"
                continue
        
            # Only execute if compilation succeeded
            try:
                print(f"Running AppleScript: {applescript_code}")
                response = input("Press Enter to continue...")
                if response != "":
                    return "User aborted"
                result = subprocess.run(['osascript', '-e', applescript_code], capture_output=True, text=True, check=True)
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                query += f"\n\nI wrote this AppleScript code:\n\n<applescript>{applescript_code}</applescript>\n\nBut I got this error when running it:\n{e.stderr.strip()}\n\nPlease write new Applescript to help me achieve my goal."
                continue

    def compile(self, applescript_code):
        """
        Check AppleScript syntax without executing it.
        Returns (is_valid, error_message)
        """
        try:
            result = subprocess.run(
                ['osacompile', '-e', applescript_code, '-o', '/dev/null'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return True, None
                
            return False, result.stderr.strip()
            
        except subprocess.SubprocessError as e:
            return False, f"Failed to run osacompile: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"