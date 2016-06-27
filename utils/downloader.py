import os.path
import hashlib
import urllib.parse
import urllib.request


class Downloader:

    """
    A general purpose downloader
    """

    @staticmethod
    def request(url, params=None, on_complete=None):
        """
        Send the HTTP GET request and returns data from specified url

        @param url: url to send the request
        @param params: parameters to pass to the url
        @param on_complete: a callback function
            if provided, method will become an async task and will callback when
                request is complete
        """
        params = params or {}
        if params:
            url += "?" + urllib.parse.urlencode(params)
        return Downloader.download(url, on_complete=on_complete)

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
                from ..threads import BackgroundThread
                return BackgroundThread(
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
                from ..threads import BackgroundThread
                return BackgroundThread(
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
