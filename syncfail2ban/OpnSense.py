# *************************************************************************
#  Copyright 2022 Dominic Porter
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#  implied. See the License for the specific language governing
#  permissions and limitations under the License
# *************************************************************************

import logging
import requests
from syncfail2ban.Firewall import Firewall

logger = logging.getLogger(__name__)


class OpnSense(object):

    def __init__(self, api_key=None, api_secret=None, host=None, verify=False):
        self._api_key = api_key
        self._api_secret = api_secret
        self._host = host
        self._verify = verify

    def api_request(self, method: str, path: str, json=None, headers=None) -> requests.Response:

        if self._verify:
            url = f"https://{self._host}/api/{path}/"
        else:
            url = f"http://{self._host}/api/{path}/"

        if headers is None:
            headers = {}

        if (method == "POST") and (json is not None):
            logger.debug(f"OpnSense: API POST - {url}")
            headers = {"Content-Type": "application/json; charset=utf-8"}
            return requests.post(url,
                                 verify=self._verify,
                                 auth=(self._api_key, self._api_secret),
                                 headers=headers,
                                 json=json)
        else:
            logger.debug(f"OpnSense: API GET - {url}")
            return requests.get(url,
                                verify=self._verify,
                                auth=(self._api_key, self._api_secret),
                                headers=headers)

    @property
    def firewall(self) -> Firewall:
        return Firewall(self)



