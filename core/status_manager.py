import sublime
import random
import string
from .settings import Settings


STATUS_NAME = "Javatar"


class StatusManager:

    """
    Status Text manager for complex status text usages
    """

    ready = False

    @staticmethod
    def animated_startup_text(status=None, animated=True):
        """
        Returns animated startup message

        @param status: status instance
        @param animated: if provided as True, will return message that
            will changed over time
        """
        if animated:
            status = status or {}
            if "frame" not in status:
                status["frame"] = 0
                status["up"] = True

            if status["up"]:
                status["frame"] += 1
            else:
                status["frame"] -= 1
            if status["frame"] == 4 or status["frame"] == 0:
                status["up"] = not status["up"]

            frame = status["frame"]
        else:
            frame = 3
        return "Javatar is starting up [%s=%s]" % (" " * frame,
                                                   " " * (4-frame))

    @staticmethod
    def reset(show_message=True):
        """
        Reset status manager (used on restart)

        WARNING: This method must not access any settings
        """
        StatusManager.status = {}
        if show_message:
            view = sublime.active_window().active_view()
            view.set_status(STATUS_NAME,
                            StatusManager.animated_startup_text(animated=False))

    @staticmethod
    def pre_startup():
        """
        Loads settings and run status manager in basic mode
            (just to show single animated status text)
        """
        StatusManager.cycle_time = Settings.get("status_cycle_delay")
        StatusManager.run()
        StatusManager.startup_status = StatusManager.show_status(StatusManager.animated_startup_text, delay=-1)

    @staticmethod
    def startup():
        """
        Loads settings and run status manager on Javatar fully ready
        """
        StatusManager.hide_status(StatusManager.startup_status)
        StatusManager.ready = True

    @staticmethod
    def ref_is_exists(ref):
        """
        Returns whether reference key is already exists or not

        @param ref: reference key
        """
        for status_name in StatusManager.status:
            status_list = StatusManager.status[status_name]["status"]
            for status in status_list:
                if ref.lower() == status["ref"].lower():
                    return True
        return False

    @staticmethod
    def remove_ref(ref):
        """
        Remove any reference key from status texts

        @param ref: reference key
        """
        for status_name in StatusManager.status:
                status_list = StatusManager.status[status_name]["status"]
                status_list = [status
                               for status in
                               status_list
                               if status["ref"].lower() != ref.lower()]
                StatusManager.status[status_name]["status"] = status_list

    @staticmethod
    def show_status(text, delay=None, ref=None, must_see=False, target=None):
        """
        Add status text to status bar and returns reference name

        @param text: if provided as string, will use as status message
            if provided as not string, will use as a callback which
            receives status instance and returns a string to be used
        @param delay: if provided more than 0, will use as message delay
            if provided less than 0, status message will be permanent
            otherwise, default value will be used
        @param ref: if provided, will use as reference name
            otherwise, this will randomly generated
        @param must_see: if provided as True, will update status on show only,
            this will ensure status text to been seen such as error messages
        @param target: if provided, will show status text on specified target
            status bar, otherwise, default status bar is used

        Reference key is case-insensitive
        """
        status = {}
        if delay is None:
            delay = Settings.get("status_delay")
            status["permanent"] = False
        else:
            status["permanent"] = delay < 0
        status["delay"] = delay
        status["must_see"] = must_see
        if ref is None:
            while ref is None or StatusManager.ref_is_exists(ref):
                ref = "".join([
                    random.choice(string.ascii_letters + string.digits)
                    for _ in range(8)
                ])
        else:
            StatusManager.remove_ref(ref)
        if isinstance(text, str):
            status["text"] = text
        else:
            status["custom"] = text
        status["ref"] = ref.lower()

        if target is None:
            target = STATUS_NAME
        else:
            target = STATUS_NAME + "_" + target
        if target not in StatusManager.status:
            StatusManager.status[target] = {"status": [], "current_cycle": 0}
        StatusManager.status[target]["status"].append(status)

        return ref

    def hide_status(ref=None):
        """
        Remove status text from status bar

        @param ref: if provided as empty string, will remove all status texts
            if provided, will use as reference key to remove all matched
            status texts

        Reference key is case-insensitive
        """
        if ref is None:
            return
        if ref == "":
            for status_name in StatusManager.status:
                StatusManager.status[status_name]["status"] = []
        else:
            for status_name in StatusManager.status:
                status_list = StatusManager.status[status_name]["status"]
                status_list = [status
                               for status in
                               status_list
                               if status["ref"].lower() != ref.lower()]
                StatusManager.status[status_name]["status"] = status_list

    @staticmethod
    def default_status():
        """
        Javatar default status provider

        Returns relative package path for current view
        """
        return "Javatar Default Status"

    @staticmethod
    def update_status(status, force=False):
        """
        Update status and returns whether to keep the status or not

        @param status: status to be updated
        @param force: if provided as True, must see status texts will be
            updated
        """
        if status["permanent"]:
            return True
        if not status["must_see"] or force:
            status["delay"] -= 100
        return status["delay"] > 0

    @staticmethod
    def run():
        """
        Update all status messages and cycle through them
        """
        view = sublime.active_window().active_view()
        for status_name in tuple(StatusManager.status.keys()):
            status_section = StatusManager.status[status_name]
            status_list = status_section["status"]
            status_list = [status
                           for status in
                           status_list
                           if StatusManager.update_status(status, False)]
            status_section["status"] = status_list
            StatusManager.status[status_name] = status_section
            if not status_list:
                if StatusManager.ready and status_name == STATUS_NAME and Settings.get("show_package_path"):
                    view.set_status(status_name, StatusManager.default_status())
                else:
                    view.erase_status(status_name)
                continue

            status_section["current_cycle"] += 100
            if status_section["current_cycle"] >= StatusManager.cycle_time:
                status_section["current_cycle"] = 0
                if status_list:
                    status_list = status_list[1:] + [status_list[0]]

            if status_list:
                status = status_list[0]
                StatusManager.update_status(status, True)
                status_text = None
                if "text" in status:
                    status_text = status["text"]
                elif "custom" in status:
                    status_text = status["custom"](status)
                if status_text is not None:
                    view.set_status(status_name, status_text)

        sublime.set_timeout(StatusManager.run, 100)
