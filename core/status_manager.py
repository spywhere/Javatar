import sublime
import random
import string
from .logger import Logger
from .settings import Settings
from .state_property import StateProperty
from .java_utils import JavaUtils
import math
import types

STATUS_NAME = "Javatar"


class _StatusManager:

    """
    Status Text manager for complex status text usages
    """

    SCROLL = "scroll"
    CYCLE = "cycle"

    @classmethod
    def instance(cls, new=False):
        if new and hasattr(cls, "_instance"):
            cls._instance.reset()
        if not hasattr(cls, "_instance") or not cls._instance or new:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.reset(show_message=False)
        self.ready = False
        self.cycle_time = 1000
        self.offset = 0
        self.scroll_size = 50

    def show_notification(self, message, title="Javatar"):
        """
        Push the notification to the system

        @param message: a notification message
        @param title: a notification caption
        """
        sublime.run_command("sub_notify", {
            "title": title,
            "msg": message,
            "sound": True
        })

    def animated_startup_text(self, status=None, animated=True):
        """
        Returns animated startup message

        @param status: status instance
        @param animated: a boolean specified whether returns message that
            will changed over time or not
        """
        chars = "⢁⡈⠔⠢"
        frame = 0
        if animated:
            status = status or {}
            if "frame" not in status:
                status["frame"] = 0
            status["frame"] += 1
            status["frame"] %= len(chars)
            frame = status["frame"]
        return "Javatar is starting up [%s]" % (chars[frame])

    def reset(self, show_message=True):
        """
        Reset status manager (used on restart)

        WARNING: This method must not access any settings
        """
        self.status = {}
        self.running = False
        view = sublime.active_window().active_view()
        view.erase_status(STATUS_NAME)
        if show_message:
            view = sublime.active_window().active_view()
            view.set_status(STATUS_NAME,
                            self.animated_startup_text(animated=False))

    def pre_startup(self):
        """
        Loads settings and run status manager in basic mode
            (just to show single animated status text)
        """
        self.cycle_time = Settings().get(
            "status_cycle_delay",
            self.cycle_time
        )
        self.scroll_size = Settings().get(
            "status_scrolling_size",
            self.scroll_size
        )
        if not self.running:
            self.running = True
            self.run()
        self.startup_status = self.show_status(
            self.animated_startup_text,
            delay=-1
        )

    def startup(self):
        """
        Loads settings and run status manager on Javatar fully ready
        """
        self.hide_status(self.startup_status)
        self.ready = True

    def ref_is_exists(self, ref):
        """
        Returns whether reference key is already exists or not

        @param ref: reference key
        """
        for status_name in self.status:
            status_list = self.status[status_name]["status"]
            for status in status_list:
                if ref.lower() == status["ref"].lower():
                    return True
        return False

    def remove_ref(self, ref):
        """
        Remove any reference key from status texts

        @param ref: reference key
        """
        for status_name in self.status:
                status_list = self.status[status_name]["status"]
                status_list = [status
                               for status in
                               status_list
                               if status["ref"].lower() != ref.lower()]
                self.status[status_name]["status"] = status_list

    def show_status(self, text, delay=None, scrolling=None,
                    ref=None, must_see=False, target=None):
        """
        Add status text to status bar and returns reference name

        @param text: a text to show
            if provided as string, will use as status message

            if provided as not string, will use as a callback which
            receives status instance and returns a string to be used
        @param delay: a status delay (showing duration)
            if provided more than 0, will use as message delay

            if provided less than 0, status message will be permanent

            otherwise, default value will be used
        @param scrolling: scrolling style
            if provided as string, this will use the default scroller style
                with default offset and size

            if provided as function, this value must receives a status text,
                status info and return a scrolled status

            if provided as list, tuple, this value should be 1 to 3-tuple/list
                (scroller, size, offset) format when scroller is either a string
                or a function, size and offset must be an int

            any invalid value will result in no scrolling
        @param ref: a reference name
            if provided, will use as reference name

            otherwise, this will randomly generated
        @param must_see: a boolean specified whether update status on show only,
            this will ensure status text to been seen such as error messages
        @param target: a status bar target name
            if provided, will show status text on specified target status bar

            otherwise, default status bar is used

        Reference key is case-insensitive
        """
        status = {}
        if delay is None:
            delay = Settings().get("status_delay")
            status["permanent"] = False
        else:
            status["permanent"] = delay < 0
        status["scroller"] = None
        status["scroll_offset"] = 0
        status["scroll_size"] = self.scroll_size
        if isinstance(scrolling, str):
            if scrolling.lower() == self.SCROLL:
                status["scroller"] = self.text_scroller
            elif scrolling.lower() == self.CYCLE:
                status["scroller"] = self.text_cycler
        elif isinstance(scrolling, list) or isinstance(scrolling, tuple):
            if len(scrolling) > 2 and isinstance(scrolling[2], int):
                status["scroll_offset"] = scrolling[2]
            if len(scrolling) > 1 and isinstance(scrolling[1], int):
                status["scroll_size"] = scrolling[1]
            if len(scrolling) > 0 and isinstance(scrolling[0], str):
                if scrolling[0].lower() == self.SCROLL:
                    status["scroller"] = self.text_scroller
                elif scrolling[0].lower() == self.CYCLE:
                    status["scroller"] = self.text_cycler
        elif isinstance(scrolling, types.FunctionType):
            status["scroller"] = scrolling
        status["delay"] = delay
        status["must_see"] = must_see
        if ref is None:
            while ref is None or self.ref_is_exists(ref):
                ref = "".join([
                    random.choice(string.ascii_letters + string.digits)
                    for _ in range(8)
                ])
        else:
            self.remove_ref(ref)
        if isinstance(text, str):
            status["text"] = text
        else:
            status["custom"] = text
        status["ref"] = ref.lower()

        if target is None:
            target = STATUS_NAME
        else:
            target = STATUS_NAME + "_" + target
        if target not in self.status:
            self.status[target] = {"status": [], "current_cycle": 0}
        self.status[target]["status"].append(status)

        return ref

    def hide_status(self, ref=None):
        """
        Remove status text from status bar

        @param ref: a reference name
            if provided as empty string, will remove all status texts

            if provided, will use as reference key to remove all matched
            status texts

        Reference key is case-insensitive
        """
        if ref is None:
            return
        if ref == "":
            for status_name in self.status:
                self.status[status_name]["status"] = []
        else:
            for status_name in self.status:
                status_list = self.status[status_name]["status"]
                status_list = [status
                               for status in
                               status_list
                               if status["ref"].lower() != ref.lower()]
                self.status[status_name]["status"] = status_list

    def default_status(self):
        """
        Javatar default status provider

        Returns relative package path for current view
        """
        if StateProperty().is_java():
            return "Package: {readable_class_path}".format_map({
                "readable_class_path": JavaUtils().to_readable_class_path(
                    StateProperty().get_dir()
                )
            })
        return ""

    def update_status(self, status, force=False):
        """
        Update status and returns whether to keep the status or not

        @param status: status to be updated
        @param force: a boolean specified whether must-see-status should be
            updated
        """
        if status["permanent"]:
            return True
        if "delay" not in status or status["delay"] is None:
            Logger().debug(
                "If you see this, please send the whole console " +
                "log to developer [StatusManager]: %s" % (str(status))
            )
            return False
        if not status["must_see"] or force:
            status["delay"] -= 100
        return status["delay"] > 0

    def text_no_scroll(self, text, status=None):
        """
        A simple text display
        """
        return text

    def text_scroller(self, text, status=None):
        """
        A simple text scroller (from right to left)
        """
        scroll_size = self.scroll_size
        if len(text) <= scroll_size:
            return text

        if status:
            status["scroll_offset"] += (scroll_size / len(text)) * 0.1
            status["scroll_offset"] %= 2 * math.pi
            offset = status["scroll_offset"]
        else:
            self.offset += 0.1
            self.offset %= 2 * math.pi
            offset = self.offset

        size = (len(text) - scroll_size) + 1
        offset = int(size / 2 + math.sin(offset) * size / 2)

        return text[offset:][:scroll_size]

    def text_cycler(self, text, status=None):
        """
        A text scroller which goes back and forth
        """
        scroll_size = self.scroll_size
        if len(text) <= scroll_size:
            return text

        if status:
            status["scroll_offset"] += 0.5
            status["scroll_offset"] %= len(text)
            offset = int(status["scroll_offset"])
        else:
            self.offset += 0.5
            self.offset %= len(text)
            offset = int(self.offset)

        return (text[offset:]+text[:offset])[:scroll_size]

    def run(self):
        """
        Update all status messages and cycle through them
        """
        if not self.running:
            return
        window = sublime.active_window()
        if not window:
            sublime.set_timeout(self.run, 100)
            return
        view = window.active_view()
        for status_name in tuple(self.status.keys()):
            status_section = self.status[status_name]
            status_list = status_section["status"]
            status_list = [status
                           for status in
                           status_list
                           if (status is not None and
                               self.update_status(status, False))]
            status_section["status"] = status_list
            self.status[status_name] = status_section
            if not status_list:
                if (self.ready and
                    status_name == STATUS_NAME and
                        Settings().get("show_package_path")):
                    view.set_status(
                        status_name,
                        self.default_status()
                    )
                else:
                    view.erase_status(status_name)
                continue

            status_section["current_cycle"] += 100
            if status_section["current_cycle"] >= self.cycle_time:
                status_section["current_cycle"] = 0
                if status_list:
                    status_list = status_list[1:] + [status_list[0]]

            if status_list:
                status = status_list[0]
                self.update_status(status, True)
                status_text = None
                if "text" in status:
                    status_text = status["text"]
                elif "custom" in status:
                    status_text = status["custom"](status)
                scroller = status["scroller"] or self.text_no_scroll
                if status_text is not None:
                    view.set_status(status_name, scroller(status_text, status))

        sublime.set_timeout(self.run, 100)


def StatusManager(new=False):
    return _StatusManager.instance(new)
