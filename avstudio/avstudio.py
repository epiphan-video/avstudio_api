import logging
import requests
import time
import os
from requests_toolbelt.utils import dump

from .avstudio_devices import Devices


class APIAccess(object):
    _address = None
    _cookies = {}
    _username = None
    _debug = False
    _current_team = None
    _user_info = None

    # Privates

    def get_full_url(self, request, noteam=False):
        request_params = {
            "host": self._address,
            "version": "v1t",
            "teamid": self._current_team if self._current_team else None,
            "request": request
        }

        if request[0] == '/':
            # Absolute path
            return "https://%(host)s%(request)s" % request_params
        else:
            # Relative paths
            if self._current_team is None or noteam:
                return "https://%(host)s/front/api/%(version)s/%(request)s" % request_params
            else:
                return "https://%(host)s/front/api/%(version)s/team/%(teamid)s/%(request)s" % request_params

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

    def http_get(self, request, noteam=False):
        start_time = time.time()
        r = requests.get(self.get_full_url(request, noteam), cookies=self._cookies)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        r.raise_for_status()
        return r

    def http_head(self, request, cookies=False, noteam=False):
        start_time = time.time()
        if cookies:
            r = requests.head(self.get_full_url(request, noteam), cookies=self._cookies)
        else:
            r = requests.head(self.get_full_url(request, noteam))
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        r.raise_for_status()
        return r

    def http_delete(self, path, noteam=False):
        start_time = time.time()
        r = requests.delete(self.get_full_url(path, noteam), cookies=self._cookies)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        r.raise_for_status()
        return r

    def http_post(self, request, noteam=False):
        start_time = time.time()
        r = requests.post(self.get_full_url(request, noteam), cookies=self._cookies)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        r.raise_for_status()
        return r

    def http_post_data(self, request, data, noteam=False):
        start_time = time.time()
        r = requests.post(self.get_full_url(request, noteam), cookies=self._cookies, json=data)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        r.raise_for_status()
        return r

    def http_put_data(self, request, data, noteam=False):
        start_time = time.time()
        r = requests.put(self.get_full_url(request, noteam), cookies=self._cookies, json=data)
        stop_time = time.time()

        self.dump_request(r, stop_time - start_time)
        r.raise_for_status()
        return r

    def http_post_file(self, request, filename, mime="application/binary", noteam=False):
        files = {"file": (os.path.basename(filename), open(filename, "rb"), mime)}
        r = requests.post(self.get_full_url(request, noteam), cookies=self._cookies, files=files)
        r.raise_for_status()
        return r

    def http_download_file(self, url, local_filename, noteam=False):
        self.logger().debug("Downloading \"%s\" to file \"%s\"" % (url, local_filename))

        r = requests.get(self.get_full_url(url, noteam), stream=True, cookies=self._cookies)
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        self.logger().debug("Downloaded \"%s\" to file \"%s\"" % (url, local_filename))

        return r

    def __init__(self, address):
        self._address = address

    def login(self, username, password, invite_token=None):
        """
        covers: GET /front/api/v1t/oauth/base/{user_id}
        """

        if self._user_info:
            self.logger().debug("Already logged in, logout first")
            self.logout()

        self._username = username
        login_url = self.get_full_url("oauth/base/%s?pwd=%s" % (username, password))

        self.logger().info("Logging in: %s", login_url)

        login_cookies = None
        if invite_token is not None:
            login_cookies = {"invite-token": invite_token}
            login_url += "&invite=yes"

        r = requests.get(login_url, allow_redirects=False, cookies=login_cookies)
        self.dump_request(r)
        r.raise_for_status()

        # Temporary code for retrieving team id
        loc = r.headers["Location"]
        self._current_team = loc.split('/')[3].strip('#')

        self._cookies = {"KSESSIONID": r.cookies["KSESSIONID"]}
        self.get_user_info()

    def get_user_info(self):
        """
        covers: GET /front/api/v1t/users/me
        """
        self._user_info = self.http_get("users/me").json()
        return self._user_info

    def logout(self):
        """
        covers: GET /front/api/v1t/oauth/logout
        """
        self._current_team = None
        logout_url = self.get_full_url("oauth/logout")
        self.logger().info("Logging out as %s", self._username)
        r = requests.get(logout_url, allow_redirects=False, cookies=self._cookies)
        self._cookies = {}
        r.raise_for_status()
        self._user_info = None

    @property
    def current_user_id(self):
        return None if self._user_info is None else self._user_info["ID"]

    @property
    def current_user_name(self):
        return None if self._user_info is None else self._user_info["Name"]

    @property
    def current_team(self):
        return self._current_team

    @current_team.setter
    def current_team(self, teamid):
        self._current_team = teamid


class AVStudioAPI(object):
    def __init__(self, address):
        self.HTTP = APIAccess(address)
        self._api_access = self.HTTP  # _api_access is obsolete

        self.Devices = Devices(self._api_access)

    def login(self, username, password, invite_token=None):
        self._api_access.login(username, password, invite_token)

    def logout(self):
        self._api_access.logout()

    @property
    def current_user_id(self):
        return self._api_access.current_user_id

    @property
    def current_user_name(self):
        return self._api_access.current_user_name

    @property
    def current_team(self):
        return self._api_access.current_team

    def delete_all(self):
        for subsys in [self.Scenes, self.Devices, self.Assets]:
            subsys.delete_all()
