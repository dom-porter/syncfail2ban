import pathlib
import subprocess
import logging
import time

import zmq
from common import *
from threading import Thread
from queue import Queue


# manage the zmq queue. decide what should be added to local sync-jail and what needs to be sent to target servers
class UpdateThread(Thread):
    def __init__(self, work_queue_, dic_jails_, mq_ip_, mq_port_, logger_):
        Thread.__init__(self)
        self.work_queue = work_queue_
        self.dic_jails = dic_jails_
        self.mq_ip = mq_ip_
        self.mq_port = mq_port_
        self.mq_context = zmq.Context()
        self.mq_socket = self.mq_context.socket(zmq.REP)
        self.logger = logger_

    def run(self):

        try:
            self.mq_socket.bind("tcp://%s:%s" % (self.mq_ip, self.mq_port))
            self.logger.info(" Started server {0}:{1}" .format(self.mq_ip, self.mq_port))

            update_is_continue = True

            while update_is_continue:
                message = self.mq_socket.recv_string()

                if message == "stop":
                    # self.logger.info(" Processing - stop")
                    self.work_queue.put("stop")
                    update_is_continue = False
                    self.mq_socket.send_string(" Server stopped")

                else:
                    # Make sure that the jail is not stopped
                    # logging.info(" Processing - {0}".format(message))
                    result = process_message(message, self.work_queue, self.dic_jails)
                    self.mq_socket.send_string(result)

            self.mq_socket.close()
            self.mq_context.term()
            self.logger.info(" Info: Server stopped")

        except zmq.ZMQError as e:
            self.logger.error(" Error: Unable to start server on IP address {0} using port {0} - {1}"
                              .format(self.mq_ip, self.mq_port, e.strerror))

        except Exception as e:
            self.logger.error(" Error: Unhandled exception - {0}".format(e))
            self.mq_socket.close()
            self.mq_context.term()


# Sync the IPs to the target servers
class SyncThread(Thread):
    def __init__(self, work_queue_, sync_list_, mq_port_, timeout_, logger_):
        Thread.__init__(self)
        self.work_queue = work_queue_
        self.sync_list = sync_list_
        self.mq_port = mq_port_
        self.timeout = timeout_
        self.logger = logger_

    def run(self):
        sync_is_continue = True

        while sync_is_continue:
            message = self.work_queue.get()
            if message == "stop":
                self.work_queue.task_done()
                sync_is_continue = False

            else:
                # sync message to all sync targets
                for ip_target in self.sync_list.split():
                    response = sync_message(ip_target, message, self.mq_port, self.timeout, self.logger)
                    if response == "1":
                        self.logger.info(" Updated fail2ban - [{0}] {1}" .format(ip_target, message))
                    else:
                        self.logger.info(" Failed to update fail2ban - [{0}] {1}".format(ip_target, message))

                self.work_queue.task_done()
                # time.sleep(1)


def process_message(str_message_, work_queue_, dic_jails_):
    # str_message content:
    # str_message_split[0] = jail name
    # str_message_split[1] = banip or unbanip
    # str_message_split[2] = IP address

    # logging.debug(" Debug: Received message - {0}" .format(str_message))

    str_message_split = str_message_.split()
    str_jail = str_message_split[0]
    str_action = str_message_split[1]
    str_ip_address = str_message_split[2]

    # if the jail name matches a name in the jail config then sync, else do nothing
    # note: jail config is in the format postfix = postfix_sync (jail name = sync jail name)

    str_sync_jail_name = dic_jails_.get(str_jail, "")

    if str_sync_jail_name != "":
        # message originated from the local server, sync required so add to work queue
        # change jail name to match the sync jail name in the new message
        modified_message = "{0} {1} {2}" .format(str_sync_jail_name, str_action, str_ip_address)
        work_queue_.put(modified_message)
        return "1"

    else:
        # message originated from external server and no sync required so add to local jail
        try:
            result = subprocess.run(
                ['fail2ban-client', 'set', str_jail, str_action, str_ip_address],
                check=True, capture_output=True, text=True)

            if str(result.stdout).strip() == "1":
                logging.info(" Info: fail2ban-client set {0} {1} {2} - Success"
                             .format(str_jail, str_action, str_ip_address))
                return "1"
            else:
                logging.error(" Error: fail2ban-client set {0} {1} {2} - Failure, check fail2ban log"
                              .format(str_jail, str_action, str_ip_address))
                return "0"

        except subprocess.CalledProcessError as e:
            str_error = str(e.stderr)
            if str_error.find("Is fail2ban running?") != -1:
                logging.error(" Error: Unable to process update to fail2ban as fail2ban is not accessible. Check that it is running.")
            else:
                logging.error(" Error: Unable to process update to fail2ban as fail2ban reported an error. Check the log for fail2ban.")
            return "0"


def sync_message(ip_target_, message_, mq_port_, timeout_, logger_):
    mq_context = zmq.Context()
    mq_socket = mq_context.socket(zmq.REQ)

    try:
        mq_socket.setsockopt(zmq.LINGER, 0)
        mq_socket.connect("tcp://%s:%s" % (ip_target_, mq_port_))
        mq_socket.send_string(message_)
        poller = zmq.Poller()
        poller.register(mq_socket, zmq.POLLIN)

        # if there is no response from the target host raise an error
        if poller.poll(int(timeout_) * 1000):
            response_msg = mq_socket.recv_string()
            poller.unregister(mq_socket)
            mq_socket.close()
            mq_context.term()
            return response_msg
        else:
            poller.unregister(mq_socket)
            mq_socket.close()
            mq_context.term()
            raise IOError("Timeout connecting to server")

    except IOError as e_io:
        logger_.error(
            " Sync failure, unable to connect to server {0}:{1} - {2}".format(ip_target_, mq_port_, e_io))
        mq_socket.close()
        mq_context.term()

    except zmq.ZMQError as e_zmq:
        logger_.error(
            " Sync failure, unable to connect to server {0}:{1} - {2}".format(ip_target_, mq_port_, e_zmq))
        mq_socket.close()
        mq_context.term()


if __name__ == '__main__':
    is_continue = True
    received_ip = SyncList(3)

    logging.basicConfig(filename="/var/log/syncfail2ban.log", level=logging.INFO, format="%(asctime)s-%(message)s")

    server_config = SyncConfig(pathlib.Path(__file__).parent.absolute().__str__() + "/" + CONFIG_FILENAME)

    logging.info(" Starting server...")

    mq_ip_address = server_config.getmq_ip()
    mq_port = server_config.getmq_port()
    sync_jails = server_config.getjail_names()
    mq_timeout = server_config.gettimeout()
    sync_targets = server_config.getsync_servers()

    work_queue = Queue()
    update_thread = UpdateThread(work_queue, sync_jails, mq_ip_address, mq_port, logging)
    sync_thread = SyncThread(work_queue, sync_targets, mq_port, mq_timeout, logging)

    update_thread.start()
    sync_thread.start()
    update_thread.join()


