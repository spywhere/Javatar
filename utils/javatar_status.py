import sublime
from .javatar_utils import (
    get_settings, is_ready, to_readable_package,
    get_current_package
)


STATUS_NAME = "Javatar"
STATUS = None


class JavatarStatus():
    delay = 0
    permtext = ""
    running = False

    def set_status(self, text, delay=None, require_java=False):
        if delay is None:
            self.delay = get_settings("status_delay")
        else:
            if delay < 0:
                self.permtext = text
            else:
                self.delay = delay
        from .javatar_validator import is_java
        if not is_java() and require_java:
            return
        view = sublime.active_window().active_view()
        view.set_status(STATUS_NAME, text)

        if not self.running:
            sublime.set_timeout(lambda: self.run(), 10)
            self.running = True

    def hide_status(self, clear=False):
        if clear:
            self.permtext = ""
        view = sublime.active_window().active_view()
        if view is not None:
            from .javatar_validator import is_java
            if is_ready() and is_java() and get_settings("show_package_path"):
                if self.permtext == "":
                    view.set_status(STATUS_NAME, "Package: " + to_readable_package(get_current_package(), True))
                else:
                    view.set_status(STATUS_NAME, self.permtext)
            elif self.permtext == "":
                view.erase_status(STATUS_NAME)
        self.running = False

    def run(self):
        self.delay -= 100
        if self.delay <= 0:
            self.hide_status()
            self.running = False
        if self.running:
            sublime.set_timeout(lambda: self.run(), 100)


def get_status():
    global STATUS
    if STATUS is None:
        STATUS = JavatarStatus()
    return STATUS
