import threading


class BuilderThread(threading.Thread):
    def __init__(self, controller, files=None, macro_data=None):
        self.files = files or []
        self.macro_data = macro_data or {}
        self.controller = controller
        self.running = True
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        while self.running and self.files:
            print("I'm running")
            break

    def cancel(self):
        self.running = False
