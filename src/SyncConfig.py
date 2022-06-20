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
        self._opn_key = self._config.get('default', 'opn_key')
        self._opn_secret = self._config.get('default', 'opn_secret')
        self._debug = self._config.getboolean('default', 'log_debug', fallback=False)

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
    def opn_key(self) -> str:
        return self._opn_key

    @property
    def opn_secret(self) -> str:
        return self._opn_secret

    @property
    def debug(self) -> bool:
        return self._debug
