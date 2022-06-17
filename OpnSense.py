import logging
import requests
from Firewall import Firewall

logger = logging.getLogger(__name__)


class OpnSense(object):

    def __init__(self, api_key=None, api_secret=None, host=None, verify=False):
        self._api_key = api_key
        self._api_secret = api_secret
        self._host = host
        self._verify = verify

    def api_request(self, method, path, json=None, headers=None) -> requests.Response:

        if self._verify:
            url = f"https://{self._host}/api/{path}/"
        else:
            url = f"http://{self._host}/api/{path}/"

        if headers is None:
            headers = {}

        if (method == "POST") and (json is not None):
            logger.debug(f"OpnSense API POST - {url}")
            headers = {"Content-Type": "application/json; charset=utf-8"}
            return requests.post(url,
                                 verify=self._verify,
                                 auth=(self._api_key, self._api_secret),
                                 headers=headers,
                                 json=json)
        else:
            logger.debug(f"OpnSense API GET - {url}")
            return requests.get(url,
                                verify=self._verify,
                                auth=(self._api_key, self._api_secret),
                                headers=headers)

    @property
    def firewall(self) -> Firewall:
        return Firewall(self)



