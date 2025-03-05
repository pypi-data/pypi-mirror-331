from .simplified_http_client import Client, Response
from .exceptions import *

class Interface(object):
    def __init__(self, host, auth):
        """
        Construct the basic Interface object for HTTP calls. 
        The HTTP client is being set up during initialization,
        changes in runtime will not affect its behaviour.
        :param host: base URL for API calls
        :type host: string
        :param auth: the authorization header
        :type auth: string
        """
        from . import __version__
        self.auth = auth
        self.host = host
        self.version = __version__
        self.useragent = 'loyalicos/{};python'.format(self.version)
        self.method = None
        self.path = None
        self.data = None
        self.json = None
        self.params = None
        self.timeout = None

        self.client = Client(
            host=self.host,
            request_headers=self._default_headers,
            version=1)

    @property
    def _default_headers(self):
        """Set the default header for a Loyalicos API call"""
        headers = {
            "Authorization": self.auth,
            "User-Agent": self.useragent,
            "Accept": 'application/json'
        }
        return headers

    def reset_request_headers(self):
        self.client.request_headers = self._default_headers

    def update_headers(self, new_headers, replace=False):
        if replace == True:
            self.client.request_headers = new_headers
        else:
            current_headers = self.client.request_headers
            current_headers.update(new_headers)
            self.client.request_headers = current_headers

    def send_request(self, method=None, path=None, json=None, data=None, params=None, timeout=None):
        self.method = method or self.method
        self.path = path or self.path
        self.data = data or self.data
        self.json = json or self.json
        self.params = params or self.params
        self.timeout = timeout or self.timeout
        if self.method == None:
            raise RequestNotReadyError
        self.response = Response(self.client.make_request(self.method, self.path, json=self.json, data=self.data, params=self.params, timeout=self.timeout))