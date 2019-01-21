
class Devices(object):
    def __init__(self, api_access):
        self._api_access = api_access

    def get_all(self):
        """
        Gets all devices, attached to this account
        covers: GET /front/api/v1t/devices
        """
        self._api_access.logger().info("Getting all devices")
        return self._api_access.http_get("devices").json()

    def get(self, device_id):
        """
        covers: GET /front/api/v1t/devices/{device}
        """
        self._api_access.logger().info("Getting device %s", device_id)
        return self._api_access.http_get("devices/" + device_id).json()

    def delete(self, device_id):
        """
        covers: DELETE /front/api/v1t/devices/{device}
        """
        self._api_access.logger().info("Deleting device %s", device_id)
        return self._api_access.http_delete("devices/" + device_id).json()

    def delete_all(self):
        self._api_access.logger().info("Deleting all devices")
        for dev in self.get_all():
            self.delete(dev["Id"])

    def run_command(self, device_id, cmd):
        """
        covers: POST /front/api/v1t/devices/batch_task
        """
        self._api_access.logger().info("Running command \"%s\" on device %s", cmd, device_id)
        cmd_desc = {"Devices": [device_id], "Task": {"cmd": cmd}}
        return self._api_access.http_post_data("devices/batch_task", cmd_desc).json()

    def add(self, device_id, name):
        """
        covers: POST /front/api/v1t/devices
        """
        self._api_access.logger().info("Adding device %s as \"%s\"", device_id, name)
        cmd_desc = {
            "DeviceID": device_id,
            "Name": name
        }

        return self._api_access.http_post_data("devices", cmd_desc).json()

    def set_name(self, device_id, name):
        """
        covers: PUT /front/api/v1t/devices/{device}
        """
        device_info = self.get(device_id)

        device_info["Name"] = name

        params = {"dev": device_id}

        self._api_access.logger().info("Renaming device %s to \"%s\"", device_id, name)
        return self._api_access.http_put_data("devices/%(dev)s" % params, device_info).json()

    def unpair(self, device_id):
        """
        covers: POST /front/api/v1t/devices/{device}/unpair
        """
        self._api_access.logger().info("Unpairing device %s", device_id)
        params = {"dev": device_id}
        return self._api_access.http_post("devices/%(dev)s/unpair" % params).json()

    def get_timeline(self, device_id, start, end):
        """
        covers: GET /front/api/v1t/devices/{device}/thumbnails?from={start}&to={end}
        """
        params = {
            "dev": device_id,
            "start": start,
            "end": end
        }

        return self._api_access.http_get("devices/%(dev)s/thumbnails?from=%(start)s&to=%(end)s" % params).json()

    def get_waveform(self, device_id, start, end):
        """
        covers: GET /front/api/v1t/media/waveform/{device}
        """
        params = {
            "d": device_id,
            "s": start,
            "e": end
        }
        return self._api_access.http_get("media/waveform/%(d)s?from=%(s)s&to=%(e)s&timeOffset=0" % params).json()

    def get_thumbnail(self, device, t1, t2):
        """
        covers: GET /front/api/v1t/devices/{device}/thumbnails
        """
        thumb_url = "devices/%s/thumbnails?from=%s&timeOffset=0&to=%s&"

        return self._api_access.http_get(thumb_url % (device, t1, t2)).json()

    def get_state_image(self, device, local_filename):
        """
        covers: GET /front/api/v1t/devices/{device}/thumbnails
        """
        state_url = "devices/%s/state.jpg"
        return self._api_access.http_download_file(state_url % device, local_filename)
