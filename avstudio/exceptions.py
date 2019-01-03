class AVStudioException(Exception):
    """Base class for AV Studio exceptions"""


class AVStudioHTTPError(AVStudioException):
    """Generic HTTP error (400-s errors)"""

    def __init__(self, response):
        self.message = "HTTP error {}: {}".format(response.status_code, response.text)
        self.status_code = response.status_code


class AVStudioUnauthorized(AVStudioException):
    """Invalid auth token"""

    def __init__(self):
        self.message = "Unauthorized (the auth token is invalid or was not specified)"


class AVStudioIsUnavailable(AVStudioHTTPError):
    """AV Studio returns 500-s"""

    def __init__(self, response):
        super.__init__(response)
        self.message = "AV Studio " + self.message
