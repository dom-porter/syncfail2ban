import logging
import threading
from syncfail2ban.OpnSense import *
from queue import Queue
from threading import Thread
from syncfail2ban.SyncConfig import SyncConfig

logger = logging.getLogger(__name__)


# Sync the IPs to the target firewalls
class SyncOPNThread(Thread):
    def __init__(self, server_config: SyncConfig, opn_work_queue: Queue):
        Thread.__init__(self)
        self._opn_work_queue = opn_work_queue
        self._server_config = server_config
        self.terminated = threading.Event()

    def run(self):
        logger.debug("SyncOPNThread: Started")

        while True:
            message = self._opn_work_queue.get()
            if message == "stop":
                self._opn_work_queue.task_done()
                break

            else:
                # sync message to all firewall targets
                for ip_firewall in self._server_config.opn_fw_ip.split():
                    logging.debug("SyncOPNThread: Processing - [{0}] {1}".format(ip_firewall, message))
                    response = self.sync_message_opn(ip_firewall, message)
                    if response == "1":
                        logger.info("[{0}] Updated firewall - {1}".format(ip_firewall, message))
                    else:
                        logger.info("[{0}] Failed to update firewall - {1}".format(ip_firewall, message))

                self._opn_work_queue.task_done()

        logger.debug("SyncOPNThread: Stopped")
        self.terminated.set()

    def sync_message_opn(self, ip_target: str, message: str):
        str_message_split = message.split()
        str_alias_name = str_message_split[0]
        str_action = str_message_split[1]
        str_ip_address = str_message_split[2]

        opnsense = OpnSense(self._server_config.opn_keys.get(f"{ip_target}_key", ""),
                            self._server_config.opn_keys.get(f"{ip_target}_secret", ""),
                            ip_target,
                            self._server_config.opn_verify)

        alias_controller = opnsense.firewall.alias_controller

        if str_action == "banip":
            output = alias_controller.add_host(str_alias_name, str_ip_address)
            if output == "done":
                return "1"
            return "0"

        if str_action == "unbanip":
            output = alias_controller.delete_host(str_alias_name, str_ip_address)
            if output == "done":
                return "1"
            return "0"

        # Default return value
        return "0"
