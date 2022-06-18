import logging
import threading
from OpnSense import *
from queue import Queue
from threading import Thread
from common import *

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
                    logging.debug("SyncOPNThread: Processing - {0} to {1}".format(message, ip_firewall))
                    response = sync_message_opn(self._server_config, ip_firewall, message)
                    if response == "1":
                        logger.info("Updated firewall - [{0}] {1}".format(ip_firewall, message))
                    else:
                        logger.info("Failed to update firewall - [{0}] {1}".format(ip_firewall, message))

                self._opn_work_queue.task_done()

        logger.debug("SyncOPNThread: Stopped")


def sync_message_opn(server_config: SyncConfig, ip_target: str, message: str):
    str_message_split = message.split()
    str_alias_name = str_message_split[0]
    str_action = str_message_split[1]
    str_ip_address = str_message_split[2]

    opnsense = OpnSense(server_config.opn_key,
                        server_config.opn_secret,
                        ip_target)

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
