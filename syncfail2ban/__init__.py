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
import time
import zmq
from syncfail2ban.UpdateThread import UpdateThread
from syncfail2ban.SyncThread import SyncThread
from syncfail2ban.SyncOPNThread import SyncOPNThread
from syncfail2ban.SyncConfig import SyncConfig
from queue import Queue
import signal

# Constants
CONFIG_FILENAME = "config.cfg"
CONFIG_PATH = "/etc/syncfail2ban"
VERSION = "0.0.1"

# Configure the global logger. Debug is enabled later once the config is read
logging.basicConfig(filename="/var/log/syncfail2ban.log",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


# Simple exception class used to trigger a shutdown
class ServiceExit(Exception):
    pass


# Function used to register with the signal handlers
def service_shutdown(sig, frame):
    raise ServiceExit


def terminate_update_thread(config: SyncConfig, message: str):
    mq_context = zmq.Context()
    mq_socket = mq_context.socket(zmq.REQ)
    mq_socket.connect("tcp://%s:%s" % (config.mq_ip, config.mq_port))
    mq_socket.send_string(message)
    response_msg = mq_socket.recv_string()
    mq_socket.close()
    mq_context.term()
    if response_msg == "stopped":
        logger.debug("syncfail2ban: UpdateThread confirmed stop")
    else:
        logger.debug("syncfail2ban: Failed to stop UpdateThread")


def main():

    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    server_config = SyncConfig(CONFIG_PATH + "/" + CONFIG_FILENAME)

    logger.info(f"====================================")
    logger.info(f"    syncfail2ban v{VERSION}")
    logger.info(f"====================================")

    # Change logging level if debug enabled in the config file
    if server_config.debug:
        logger.setLevel(logging.DEBUG)

    work_queue = Queue()
    opn_work_queue = Queue()

    update_thread = UpdateThread(server_config, work_queue, opn_work_queue)
    sync_thread = SyncThread(server_config, work_queue)
    opn_sync_thread = SyncOPNThread(server_config, opn_work_queue)

    threads = []

    try:
        update_thread.start()
        threads.append(update_thread)
        sync_thread.start()
        threads.append(sync_thread)

        opn_sync_thread.start()
        threads.append(opn_sync_thread)

        while True:
            time.sleep(0.5)

    except ServiceExit:
        # update_thread.shutdown_flag.set()
        # sync_thread.shutdown_flag.set()
        # opn_sync_thread.shutdown_flag.set()

        # Tell UpdateThread to stop, which will stop all the other threads
        terminate_update_thread(server_config, "stop_all")

        update_thread.join()
        sync_thread.join()
        opn_sync_thread.join()

    logger.info("Server shutdown")


if __name__ == '__main__':
    main()
