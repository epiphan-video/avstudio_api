import logging
import requests
import time
import os
from requests_toolbelt.utils import dump

from .avstudio_devices import Devices
from .exceptions import *


class APIAccess2(object):
    _host = None
    _cookies = {}
    _headers = None

    # Privates

    def get_full_url(self, request):
        request_params = {
            "host": self._host,
            "version": "v2",
            "request": request
        }

        if request[0] == '/':
            # Absolute path
            return "https://%(host)s%(request)s" % request_params
        else:
            return "https://%(host)s/front/api/%(version)s/%(request)s" % request_params

    def logger(self):
        return logging.getLogger("avstudio")

    def dump_request(self, r, request_time=None):
        request_dump = dump.dump_all(r)
        if request_time is not None:
            request_dump = request_dump.decode('ascii')
            request_dump += "\nRequest processed in {} seconds".format(request_time)

        if r.status_code in (200, 302):
            self.logger().debug(request_dump)
        else:
            self.logger().error(request_dump)

    def _raise_for_status(self, r):
        if r.status_code in (200, 302):
            return

        if r.status_code == 401:
            raise AVStudioUnauthorized()
        elif r.status_code in range(500, 600):
            raise AVStudioIsUnavailable(r)
        else:
            raise AVStudioHTTPError(r)

    def http_get(self, request):
        start_time = time.time()
        r = requests.get(self.get_full_url(request), headers=self._headers)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        self._raise_for_status(r)
        return r

    def http_head(self, request, cookies=False):
        start_time = time.time()
        if cookies:
            r = requests.head(self.get_full_url(request), headers=self._headers)
        else:
            r = requests.head(self.get_full_url(request))
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        self._raise_for_status(r)
        return r

    def http_delete(self, path):
        start_time = time.time()
        r = requests.delete(self.get_full_url(path), headers=self._headers)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        self._raise_for_status(r)
        return r

    def http_post(self, request):
        start_time = time.time()
        r = requests.post(self.get_full_url(request), headers=self._headers)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        self._raise_for_status(r)
        return r

    def http_post_data(self, request, data):
        start_time = time.time()
        r = requests.post(self.get_full_url(request), headers=self._headers, json=data)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        self._raise_for_status(r)
        return r

    def http_put_data(self, request, data):
        start_time = time.time()
        r = requests.put(self.get_full_url(request), headers=self._headers, json=data)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        self._raise_for_status(r)
        return r

    def http_post_file(self, request, filename, mime="application/binary"):
        files = {"file": (os.path.basename(filename), open(filename, "rb"), mime)}
        r = requests.post(self.get_full_url(request), headers=self._headers, files=files)
        self._raise_for_status(r)
        return r

    def http_download_file(self, url, local_filename):
        self.logger().debug("Downloading \"%s\" to file \"%s\"" % (url, local_filename))

        r = requests.get(self.get_full_url(url), stream=True, headers=self._headers)
        self._raise_for_status(r)
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        self.logger().debug("Downloaded \"%s\" to file \"%s\"" % (url, local_filename))

        return r

    def __init__(self, host):
        self._host = host

    def setAuthToken(self, token):
        self._headers = {
            "Authorization": "Bearer " + token
        }

        self.get_user_info()

    def get_user_info(self):
        """
        covers: GET /front/api/v1/users/me
        """
        return self.http_get("users/me").json()


class AVStudioAPI2(object):
    def __init__(self, host="go.avstudio.com"):
        self.HTTP = APIAccess2(host)
        self.Devices = Devices(self.HTTP)

    def setAuthToken(self, token):
        self.HTTP.setAuthToken(token)
