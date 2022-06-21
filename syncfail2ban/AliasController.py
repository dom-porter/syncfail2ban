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

import json
import requests
import logging

logger = logging.getLogger(__name__)


class AliasController(object):

    def __init__(self, device):
        self._device = device

    # Add a host IP to the content of the alias alias_name
    def add_host(self, alias_name: str, host_ip: str) -> str:
        data = {"address": host_ip}
        try:
            response = self._device.api_request("POST",
                                                f"firewall/alias_util/add/{alias_name}",
                                                data)

            if response.status_code == 200:
                response_json = json.loads(response.text)
                return response_json["status"]
            else:
                response.raise_for_status()

        except requests.HTTPError as exception:
            logger.error(f"AliasController::add_host - {exception}")

        return "failed"

    # Removes a host IP from the content of the alias alias_name
    def delete_host(self, alias_name: str, host_ip: str) -> str:
        data = {"address": host_ip}
        try:
            response = self._device.api_request("POST",
                                                f"firewall/alias_util/delete/{alias_name}",
                                                data)
            if response.status_code == 200:
                response_json = json.loads(response.text)
                return response_json["status"]
            else:
                response.raise_for_status()

        except requests.HTTPError as exception:
            logger.error(f"AliasController::delete_host - {exception}")

        return "failed"

    # Returns the UUID for a given alias name
    def get_uuid(self, alias_name: str) -> str:
        response = self._device.api_request("GET",
                                            f"firewall/alias/getAliasUUID/{alias_name}")

        response_json = json.loads(response.text)
        if "uuid" in response_json:
            return response_json['uuid']
        return None

    # Flushes an alias? Does not seem to work
    def flush(self, alias_name: str):
        try:
            response = self._device.api_request("POST",
                                                f"firewall/alias_util/flush/{alias_name}")
            if response.status_code == 200:
                response_json = json.loads(response.text)
                if "status" in response_json:
                    return response_json["status"]

        except requests.HTTPError as exception:
            logger.error(f"AliasController::flush - {exception}")

    # Returns a list of all the host IPs from the content of alias_name
    def get_content(self, alias_name: str):
        response = self._device.api_request("GET",
                                            f"firewall/alias_util/list/{alias_name}")
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if "rows" in response_json:
                return response_json["rows"]
        return None

    # Returns a list of all the aliases
    def get_list(self):
        response = self._device.api_request("GET",
                                            f"firewall/alias_util/aliases")
        if response.status_code == 200:
            response_json = json.loads(response.text)
            return response_json
        return None

    # Returns s list of alias names where ip_address appears in the content of the alias
    def find_ip(self, ip_address: str) -> list:
        data = {"ip": ip_address}
        response = self._device.api_request("POST",
                                            f"firewall/alias_util/findReferences",
                                            data)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if "matches" in response_json:
                return response_json["matches"]
        return None

    # Searches all aliases?? Can't get to work
    def search(self, search_type: str):
        data = {"type": search_type}

        response = self._device.api_request("GET",
                                            f"firewall/alias/searchItem",
                                            data)
        print(response.text)
        return response

    # Returns the details of the alias for a given UUID
    def get_details(self, uuid: str) -> dict:
        try:
            response = self._device.api_request("GET",
                                                f"firewall/alias/getItem/{uuid}")

            if response.status_code == 200:
                response_json = json.loads(response.text)
                return response_json
            else:
                response.raise_for_status()

        except requests.HTTPError as exception:
            logger.error(f"AliasController::get_details - {exception}")
        return None

    # Returns the state (enabled/disabled) of a given alias_name
    def get_state(self, alias_name: str) -> bool:
        uuid = self.get_uuid(alias_name)
        alias_details = self.get_details(uuid)

        if alias_details is not None:
            if "enabled" in alias_details["alias"]:
                return bool(int(alias_details["alias"]["enabled"]))

        return False

    # Toggles the state (enabled/disabled) for a given alias name
    # If no state is supplied the current state is retrieved
    # Broken?
    def toggle_state(self, alias_name, enabled=None):
        uuid = self.get_uuid(alias_name)
        if enabled is None:
            enabled = self.get_state(alias_name)

        response = self._device.api_request("POST",
                                            f"firewall/alias/toggleItem/bugger?enabled={not enabled}")

        return response.text









