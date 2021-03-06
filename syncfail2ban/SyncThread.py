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
import threading
import zmq
from queue import Queue
from threading import Thread
from syncfail2ban.SyncConfig import SyncConfig

logger = logging.getLogger(__name__)


# Sync the IPs to the target servers
class SyncThread(Thread):
    def __init__(self, server_config: SyncConfig, work_queue: Queue):
        Thread.__init__(self)
        self._server_config = server_config
        self._work_queue = work_queue
        self.terminated = threading.Event()

    def run(self):
        logger.debug("SyncThread: Started")

        while True:
            message = self._work_queue.get()
            if message == "stop":
                self._work_queue.task_done()
                break

            else:
                # sync message to all sync targets

                for ip_target in self._server_config.sync_servers.split():
                    logger.debug("SyncThread: Processing - [{0}] {1}".format(ip_target, message))

                    response = self.sync_message(ip_target, message)
                    if response == "1":
                        logger.info("[{0}] Updated fail2ban - {1}".format(ip_target, message))
                    else:
                        logger.info("[{0}] Failed to update fail2ban - {1}".format(ip_target, message))

                self._work_queue.task_done()

        logger.debug("SyncThread: Stopped")
        self.terminated.set()

    def sync_message(self, ip_target: str, message: str):
        mq_context = zmq.Context()
        mq_socket = mq_context.socket(zmq.REQ)

        try:
            mq_socket.setsockopt(zmq.LINGER, 0)
            mq_socket.connect("tcp://%s:%s" % (ip_target, self._server_config.mq_port))
            mq_socket.send_string(message)
            poller = zmq.Poller()
            poller.register(mq_socket, zmq.POLLIN)

            # if there is no response from the target host raise an error
            if poller.poll(int(self._server_config.timeout) * 1000):
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
            logger.error(
                "Sync failure, unable to connect to server {0}:{1} - {2}".format(ip_target, self._server_config.mq_port, e_io))
            mq_socket.close()
            mq_context.term()

        except zmq.ZMQError as e_zmq:
            logger.error(
                "Sync failure, unable to connect to server {0}:{1} - {2}".format(ip_target, self._server_config.mq_port, e_zmq))
            mq_socket.close()
            mq_context.term()
