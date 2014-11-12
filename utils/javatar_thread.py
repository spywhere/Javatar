import sublime


class MultiThreadProgress():
    thread_list = []

    def __init__(self, message="", success_message=None, on_complete=None, on_all_complete=None, anim_fx=None):
        self.message = message
        self.success_message = success_message
        self.on_complete = on_complete
        self.on_all_complete = on_all_complete
        self.all_success = True
        self.running = False
        self.outmsg = ""
        if anim_fx is not None:
            self.anim_fx = anim_fx

    def add(self, thread, message):
        self.thread_list.append([thread, message])

    def set_message(self, message):
        self.message = message

    def get_message(self):
        return self.outmsg

    def anim_fx(self, i):
        index = len(self.thread_list)
        multiple = index > 1
        msg = self.message
        for thread, message in self.thread_list:
            if multiple:
                if index == 1:
                    msg += " and "
                elif index < len(self.thread_list):
                    msg += ", "
            msg += message
            if hasattr(thread, "message"):
                msg += thread.message
            index -= 1
        return {"i": (i + 1) % 3, "message": msg + ("." * (i + 1)), "delay": 300}

    def run(self, i=0):
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
                sublime.status_message(self.success_message)
            return

        info = self.anim_fx(i)
        self.outmsg = info["message"]
        sublime.status_message(info["message"])
        sublime.set_timeout(lambda: self.run(info["i"]), info["delay"])


class ThreadProgress():
    def __init__(self, thread, message, success_message=None, anim_fx=None):
        self.thread = thread
        self.message = message
        self.success_message = success_message
        if anim_fx is not None:
            self.anim_fx = anim_fx
        sublime.set_timeout(lambda: self.run(0), 100)

    def anim_fx(self, i, message, thread):
        return {"i": (i+1) % 3, "message": "%s %s" % (self.message, "." * (i+1)), "delay": 300}

    def run(self, i):
        if not self.thread.is_alive():
            if hasattr(self.thread, "result") and not self.thread.result:
                if hasattr(self.thread, "result_message"):
                    sublime.status_message(self.thread.result_message)
                else:
                    sublime.status_message("")
                return
            if self.success_message is not None:
                sublime.status_message(self.success_message)
            return
        info = self.anim_fx(i, self.message, self.thread)
        tmsg = ""
        if hasattr(self.thread, "msg"):
            tmsg = self.thread.msg
        sublime.status_message(info["message"]+tmsg)
        sublime.set_timeout(lambda: self.run(info["i"]), info["delay"])


class SilentThreadProgress():
    def __init__(self, thread, on_complete):
        self.thread = thread
        self.on_complete = on_complete
        sublime.set_timeout(lambda: self.run(), 100)

    def run(self):
        if not self.thread.is_alive():
            self.on_complete(self.thread)
            if hasattr(self.thread, "result") and not self.thread.result:
                if hasattr(self.thread, "result_message"):
                    sublime.status_message(self.thread.result_message)
                else:
                    sublime.status_message("")
            return
        sublime.set_timeout(lambda: self.run(), 100)
