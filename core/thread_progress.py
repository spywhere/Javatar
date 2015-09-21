import sublime
from .status_manager import StatusManager


class MultiThreadProgress:

    """
    Multi-threading progress listener
    """

    def __init__(self, message="", success_message=None, on_complete=None,
                 on_all_complete=None, anim_fx=None,
                 target=None):
        self.running = False
        self.thread_list = []
        self.message = message
        self.target = target or "ThreadProgress"
        self.success_message = success_message
        self.on_complete = on_complete
        self.on_all_complete = on_all_complete
        self.all_success = True
        self.anim_fx = anim_fx or self.animation
        StatusManager().show_status(
            lambda status: self.anim_fx(status, self.get_message()),
            ref="ThreadProgress",
            target=self.target,
            delay=-1
        )

    def add(self, thread, message):
        """
        Add thread to the list

        @param thread: thread to be added
        @param message: message to be show
        """
        self.thread_list.append([thread, message])

    def set_message(self, message):
        """
        Sets main message

        @param message: message to be set
        """
        self.message = message

    def get_message(self):
        """
        Returns processed message
        """
        index = len(self.thread_list)
        multiple = index > 1
        msg = self.message
        for thread, message in self.thread_list:
            if message:
                if multiple:
                    if index == 1:
                        msg += " and "
                    elif index < len(self.thread_list):
                        msg += ", "
                msg += message
            if hasattr(thread, "message"):
                msg += thread.message
            index -= 1
        return msg

    def animation(self, status, message):
        """
        Returns message that changed over time

        @param status: status instance
        @param message: processed message
        """
        chars = "⢁⡈⠔⠢"
        if "frame" not in status:
            status["frame"] = 0

        status["frame"] += 1
        status["frame"] %= len(chars)
        return "%s [%s]" % (message, chars[status["frame"]])

    def run(self):
        """
        Check for thread progress
        """
        self.running = True
        alive = False
        index = 0
        for thread, message in self.thread_list:
            if not thread.is_alive():
                if self.on_complete is not None:
                    del self.thread_list[index]
                    self.on_complete(thread)
                if hasattr(thread, "result") and not thread.result:
                    self.all_success = False
            else:
                index += 1
                alive = True
        if not alive:
            if self.on_all_complete is not None:
                self.on_all_complete()
            if self.success_message is not None:
                StatusManager().show_status(
                    self.success_message,
                    ref="ThreadProgress",
                    target=self.target
                )
            else:
                StatusManager().hide_status("ThreadProgress")
            return

        sublime.set_timeout(self.run, 100)


class ThreadProgress:

    """
    Single thread progress listener
    """

    def __init__(self, thread, message, success_message=None, on_done=None,
                 anim_fx=None, target=None):
        self.thread = thread
        self.message = message
        self.target = target or "ThreadProgress"
        self.success_message = success_message
        self.on_done = on_done
        self.anim_fx = anim_fx or self.animation
        StatusManager().show_status(
            lambda status: self.anim_fx(status, self.get_message()),
            ref="ThreadProgress",
            target=self.target,
            delay=-1
        )
        self.run()
        if not thread.is_alive():
            thread.start()

    def get_message(self):
        """
        Returns processed message
        """
        tmsg = ""
        if hasattr(self.thread, "msg"):
            tmsg = self.thread.msg
        return self.message + tmsg

    def animation(self, status, message):
        """
        Returns message that changed over time

        @param status: status instance
        @param message: processed message
        """
        chars = "⢁⡈⠔⠢"
        if "frame" not in status:
            status["frame"] = 0

        status["frame"] += 1
        status["frame"] %= len(chars)
        return "%s [%s]" % (message, chars[status["frame"]])

    def run(self):
        """
        Check for thread progress
        """
        if not self.thread.is_alive() and hasattr(self.thread, "result"):
            if self.thread.result:
                if self.on_done is not None:
                    self.on_done()
                if self.success_message is not None:
                    StatusManager().show_status(
                        self.success_message,
                        ref="ThreadProgress",
                        target=self.target
                    )
                else:
                    StatusManager().hide_status("ThreadProgress")
            else:
                if hasattr(self.thread, "result_message"):
                    StatusManager().show_status(
                        self.thread.result_message,
                        ref="ThreadProgress",
                        target=self.target
                    )
                else:
                    StatusManager().hide_status("ThreadProgress")
            return
        sublime.set_timeout(self.run, 100)


class SilentThreadProgress:

    """
    Single thread progress listener without progression
    """

    def __init__(self, thread, on_complete, target=None):
        self.thread = thread
        self.on_complete = on_complete
        self.target = target or "ThreadProgress"
        sublime.set_timeout(lambda: self.run(), 100)
        if not thread.is_alive():
            thread.start()

    def run(self):
        """
        Check for thread progress
        """
        if not self.thread.is_alive():
            self.on_complete(self.thread)
            if hasattr(self.thread, "result") and not self.thread.result:
                if hasattr(self.thread, "result_message"):
                    StatusManager().show_status(
                        self.thread.result_message,
                        ref="ThreadProgress",
                        target=self.target
                    )
            return
        sublime.set_timeout(lambda: self.run(), 100)
