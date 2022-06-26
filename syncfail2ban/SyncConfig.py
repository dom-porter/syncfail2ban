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

import configparser
import socket


def getipv4() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.255.255.255', 1))
        host_ip = s.getsockname()[0]

    except Exception:
        host_ip = "127.0.0.1"
    finally:
        s.close()
    return host_ip


# wrapper class for the config file
class SyncConfig(object):

    def __init__(self, path):
        self._config = configparser.ConfigParser()
        self._config.read(path)
        self._is_f2b_sync = self._config.getboolean('default', 'f2b_sync', fallback=False)
        self._mq_port = self._config.get('default', 'mq_port', fallback="18862")
        self._timeout = self._config.get('default', 'connection_timeout', fallback="10")
        self._sync_servers = self._config.get('default', 'sync_servers', fallback="")
        self._mq_ip = self._config.get('default', 'mq_ip')
        if self._mq_ip == "":
            self._mq_ip = getipv4()
        self._jail_names = dict(self._config['jails'])
        self._is_opn_sync = self._config.getboolean('default', 'opn_fw_sync', fallback=False)
        self._opn_fw_ip = self._config.get('default', 'opn_fw_ip', fallback="")
        self._opn_verify = self._config.getboolean('default', 'opn_verify', fallback=False)
        self._opn_aliases = dict(self._config['opn_aliases'])
        self._opn_keys = dict(self._config['opn_keys'])
        self._debug = self._config.getboolean('default', 'log_debug', fallback=False)
        self._log_size = self._config.getint('default', 'log_max_size', fallback=0)
        self._log_backups = self._config.getint('default', 'log_backup_count', fallback=0)

    @property
    def is_f2b_sync(self) -> bool:
        return self._is_f2b_sync

    @property
    def mq_port(self) -> str:
        return self._mq_port

    @property
    def timeout(self) -> str:
        return self._timeout

    @property
    def sync_servers(self) -> str:
        return self._sync_servers

    @property
    def mq_ip(self) -> str:
        return self._mq_ip

    @property
    def jail_names(self) -> dict:
        return self._jail_names

    @property
    def is_opn_sync(self) -> bool:
        return self._is_opn_sync

    @property
    def opn_fw_ip(self) -> str:
        return self._opn_fw_ip

    @property
    def opn_verify(self) -> bool:
        return self._opn_verify

    @property
    def opn_aliases(self) -> dict:
        return self._opn_aliases

    @property
    def opn_keys(self) -> dict:
        return self._opn_keys

    @property
    def debug(self) -> bool:
        return self._debug

    @property
    def log_size(self) -> int:
        if self._log_size == 0:
            return 500000
        return self._log_size

    @property
    def log_backups(self) -> int:
        if self._log_backups == 0:
            return 1
        return self._log_backups
