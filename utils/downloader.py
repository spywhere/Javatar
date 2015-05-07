import os.path
import threading
import hashlib
import urllib


class Downloader:

    """
    A general purpose downloader
    """

    @staticmethod
    def download(url, checksum=None, on_complete=None):
        """
        Download and returns data from specified url

        @param url: url to download
        @param checksum: a checksum of data
            if provided, will check the checksum of data with specified checksum
        @param on_complete: a callback function
            if provided, method will become an async task and will callback when
                download is complete
        """
        try:
            if on_complete:
                return DownloaderThread(
                    func=Downloader.download,
                    args=[url, checksum, None],
                    on_complete=on_complete
                )
            else:
                urllib.request.install_opener(
                    urllib.request.build_opener(urllib.request.ProxyHandler())
                )
                data = urllib.request.urlopen(url).read()
                if checksum and hashlib.sha256(data).hexdigest() != checksum:
                    return None
                return data
        except Exception as e:
            raise e

    @staticmethod
    def download_file(url, path=None, checksum=None, on_complete=None):
        """
        Download and store data to file from specified url

        @param url: url to download
        @param path: file path to store data
        @param checksum: a data checksum
            if provided, will check the checksum of data with specified checksum
        @param on_complete: a callback function
            if provided, method will become an async task and will callback when
                download is complete
        """
        try:
            if on_complete:
                return DownloaderThread(
                    func=Downloader.download_file,
                    args=[url, path, checksum, None],
                    on_complete=on_complete
                )
            else:
                data = Downloader.download(url)
                if checksum and hashlib.sha256(data).hexdigest() != checksum:
                    return None
                path = path or os.path.basename(url)
                f = open(path, "wb")
                f.write(data)
                f.close()
                return os.path.exists(path)
        except Exception as e:
            raise e


class DownloaderThread(threading.Thread):

    """
    A downloader background thread
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
        except Exception as e:
            raise e
