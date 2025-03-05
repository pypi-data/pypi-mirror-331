import requests
from .exceptions import *

class Response(object):
    """ Holds the Response from API Calls """
    def __init__(self, response, format="json"):
        """
        :param response: The return value from an api call
                         from a requests call
        :type response:  requests Response object
        :param format: The return value expected format
        :type format:  String (Supported: "json")
        """
        self._status_code = response.status_code
        self._body_format = format
        if self._body_format == "json":
            self._body = response.json()
        self._headers = response.headers

    @property
    def status_code(self):
        """
        :return: integer, status code of API call
        """
        return self._status_code

    @property
    def body_format(self):
        """
        :return: string, body expected format
        """
        return self._body_format

    @property
    def body(self):
        """
        :return: any, content of the response in the expected format
        """
        return self._body

    @property
    def headers(self):
        """
        :return: dict, response headers
        """
        return self._headers

class Client(object):
    """Wrap access to API Endpoints."""

    def __init__(self,
                 host,
                 request_headers=None,
                 version=None):
        """
        :param host: Base URL for the api. (e.g. https://services.loyalicos.com/api/)
        :type host:  string
        :param request_headers: A dictionary of the headers you want
                                applied on all calls
        :type request_headers: dictionary
        :param version: The version number of the API.
        :type version: integer
        :param url_path: A list of the url path segments
        :type url_path: list of strings
        """
        self.host = host
        self.request_headers = request_headers or {}
        self._version = version
        
    def _build_versioned_url(self, url):
        """Applies the version to the url
        :param url: URI portion of the full URL being requested
        :type url: string
        :return: string
        """
        return '{}/v{}{}'.format(self.host, str(self._version), url)


    def make_request(self, method: str, path: list, json=None, data={}, params={}, timeout=None):
        """Make the API call and return the response.
        :param timeout: timeout value or None
        :type timeout: float
        :return: urllib response
        """
        timeout = timeout
        url = f'{self.host}/{"/".join(path)}'
        return requests.request(method, url, params=params, json=json, data=data, headers=self.request_headers, timeout=timeout)