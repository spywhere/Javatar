import threading


class BackgroundThread(threading.Thread):

    """
    A general purpose background thread
    """

    def __init__(self, func, args, on_complete):
        self.func = func
        self.args = args
        self.on_complete = on_complete
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        try:
            data = self.func(*self.args)
            if self.on_complete:
                self.on_complete(data)
            self.result = True
        except Exception as e:
            self.result = False
            raise e
