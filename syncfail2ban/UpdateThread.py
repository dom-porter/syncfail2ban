import subprocess
import logging
import threading
import zmq
from threading import Thread
from queue import Queue
from syncfail2ban.SyncConfig import SyncConfig

logger = logging.getLogger(__name__)


# manage the zmq queue. decide what should be added to local sync-jail and what needs to be sent to target servers
class UpdateThread(Thread):
    def __init__(self, server_config: SyncConfig, work_queue: Queue, opn_work_queue: Queue):
        Thread.__init__(self)
        self._server_config = server_config
        self._work_queue = work_queue
        self._opn_work_queue = opn_work_queue
        self._mq_context = zmq.Context()
        self._mq_socket = self._mq_context.socket(zmq.REP)
        self.terminated = threading.Event()

    def run(self):
        logger.debug("UpdateThread: Started")

        try:
            self._mq_socket.bind("tcp://%s:%s" % (self._server_config.mq_ip, self._server_config.mq_port))
            logger.info("Started server {0}:{1}".format(self._server_config.mq_ip, self._server_config.mq_port))

            while True:
                message = self._mq_socket.recv_string()

                if message == "stop_all":
                    logger.debug("UpdateThread: Stopping all threads")
                    self._work_queue.put("stop")
                    self._opn_work_queue.put("stop")
                    self._mq_socket.send_string("stopped")
                    break

                elif message == "stop":
                    logger.debug("UpdateThread: Stopping")
                    self._mq_socket.send_string("stopped")
                    break

                else:
                    logger.debug("UpdateThread: Processing message - {0}".format(message))
                    self.process_message(message)
                    self._mq_socket.send_string("1")

            self._mq_socket.close()
            self._mq_context.term()
            self.terminated.set()

        except zmq.ZMQError as e:
            logger.error("Unable to start server on IP address {0} using port {0} - {1}"
                         .format(self._server_config.mq_ip, self._server_config.mq_port, e.strerror))

        except Exception as e:
            logger.error("Unhandled exception - {0}".format(e))
            self._mq_socket.close()
            self._mq_context.term()

    def process_message(self, str_message: str):
        # str_message content:
        # str_message_split[0] = jail name
        # str_message_split[1] = banip or unbanip
        # str_message_split[2] = IP address

        # logging.debug("Debug: Received message - {0}" .format(str_message))

        str_message_split = str_message.split()
        str_jail = str_message_split[0]
        str_action = str_message_split[1]
        str_ip_address = str_message_split[2]

        # check if the ip_address should be added to the firewalls
        if self._server_config.is_opn_sync:
            str_opn_alias = self._server_config.opn_aliases.get(str_jail, "")
            if not str_opn_alias == "":
                opn_message = "{0} {1} {2}".format(str_opn_alias, str_action, str_ip_address)
                self._opn_work_queue.put(opn_message)

        if not self._server_config.is_f2b_sync:
            return

        # if the jail name matches a name in the jail config then sync, else do nothing
        # note: jail config is in the format postfix = postfix_sync (jail name = sync jail name)

        str_sync_jail_name = self._server_config.jail_names.get(str_jail, "")

        if str_sync_jail_name != "":
            # message originated from the local server, sync required so add to work queue
            # change jail name to match the sync jail name in the new message
            modified_message = "{0} {1} {2}".format(str_sync_jail_name, str_action, str_ip_address)
            self._work_queue.put(modified_message)

        else:
            # message originated from external server and no sync required so add to local jail
            try:
                result = subprocess.run(
                    ['fail2ban-client',
                     'set',
                     str_jail,
                     str_action,
                     str_ip_address],
                    check=True,
                    capture_output=True,
                    text=True)

                if str(result.stdout).strip() == "1":
                    logger.info("Updating local server: fail2ban-client set {0} {1} {2} - Success"
                                .format(str_jail, str_action,  str_ip_address))
                else:
                    logger.error("Updating local server: fail2ban-client set {0} {1} {2} - Failure, check fail2ban log"
                                 .format(str_jail, str_action, str_ip_address))

            except subprocess.CalledProcessError as e:
                str_error = str(e.stderr)
                if str_error.find("Is fail2ban running?") != -1:
                    logger.error(
                        "Error: Unable to process update to fail2ban as fail2ban is not accessible. Check that it is running.")
                else:
                    logger.error(
                        "Error: Unable to process update to fail2ban as fail2ban reported an error. Check the log for fail2ban.")
