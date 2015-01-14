import os.path
import threading
import urllib


class Downloader:
    @staticmethod
    def download(url, on_complete=None):
        if on_complete:
            return DownloaderThread(
                func=Downloader.download,
                args=[url, None],
                on_complete=on_complete
            )
        else:
            urllib.request.install_opener(
                urllib.request.build_opener(urllib.request.ProxyHandler())
            )
            return urllib.request.urlopen(url).read()

    @staticmethod
    def download_file(url, path=None, on_complete=None):
        if on_complete:
            return DownloaderThread(
                func=Downloader.download_file,
                args=[url, path, None],
                on_complete=on_complete
            )
        else:
            path = path or os.path.basename(url)
            f = open(path, "wb")
            f.write(Downloader.download(url))
            f.close()


class DownloaderThread(threading.Thread):
    def __init__(self, func, args, on_complete):
        self.func = func
        self.args = args
        self.on_complete = on_complete
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        data = self.func(*self.args)
        if self.on_complete:
            self.on_complete(data)
