import json
import os
from .ai.ai import Ai
from .browser.browser import Browser
from .calendar.calendar import Calendar
from .clipboard.clipboard import Clipboard
from .contacts.contacts import Contacts
from .display.display import Display
from .docs.docs import Docs
from .files.files import Files
from .keyboard.keyboard import Keyboard
from .mail.mail import Mail
from .mouse.mouse import Mouse
from .os.os import Os
from .skills.skills import Skills
from .sms.sms import SMS
from .vision.vision import Vision
from .audio.audio import Audio
from .siri.siri import Siri
from .document.document import Document
from .image.image import Image
from .video.video import Video
# from .ui.ui import Ui

class Computer:
    def __init__(self):

        self.offline = False
        self.verbose = False
        self.debug = False

        self.mouse = Mouse(self)
        self.keyboard = Keyboard(self)
        self.display = Display(self)
        self.clipboard = Clipboard(self)
        self.mail = Mail(self)
        self.sms = SMS(self)
        self.calendar = Calendar(self)
        self.contacts = Contacts(self)
        self.browser = Browser(self)
        self.os = Os(self)
        self.vision = Vision(self)
        self.skills = Skills(self)
        self.docs = Docs(self)
        self.ai = Ai(self)
        self.files = Files(self)
        self.audio = Audio(self)
        self.siri = Siri(self)
        self.document = Document(self)
        self.image = Image(self)
        self.video = Video(self)
        # self.ui = Ui(self)
        self.emit_images = True
        self.save_skills = True

        self.import_computer_api = False  # Defaults to false
        self._has_imported_computer_api = False  # Because we only want to do this once

        self.import_skills = False
        self._has_imported_skills = False

    @property
    def api_base(self):
        api_base = os.environ.get('INTERPRETER_API_BASE')
        if api_base is None:
            raise ValueError("INTERPRETER_API_BASE environment variable is not set")
        return api_base.rstrip("/")

    @property
    def api_key(self):
        api_key = os.environ.get('INTERPRETER_API_KEY')
        if api_key is None:
            raise ValueError("INTERPRETER_API_KEY environment variable is not set")
        return api_key

    def screenshot(self, *args, **kwargs):
        """
        Shortcut for computer.display.screenshot
        """
        return self.display.screenshot(*args, **kwargs)

    def view(self, *args, **kwargs):
        """
        Shortcut for computer.display.screenshot
        """
        return self.display.screenshot(*args, **kwargs)

    def to_dict(self):
        def json_serializable(obj):
            try:
                json.dumps(obj)
                return True
            except:
                return False

        return {k: v for k, v in self.__dict__.items() if json_serializable(v)}

    def load_dict(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
