import pathlib
import logging
import time
import zmq
from UpdateThread import UpdateThread
from SyncThread import SyncThread
from SyncOPNThread import SyncOPNThread
from common import SyncConfig
from queue import Queue
import signal

# Constants
CONFIG_FILENAME = "config.cfg"
VERSION = "Beta:17062022"

logging.basicConfig(filename="/var/log/syncfail2ban.log",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


class ServiceExit(Exception):
    pass


def service_shutdown(signum, frame):
    raise ServiceExit


def main():

    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    server_config = SyncConfig(pathlib.Path(__file__).parent.absolute().__str__() + "/" + CONFIG_FILENAME)

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

    try:
        update_thread.start()
        sync_thread.start()
        opn_sync_thread.start()

        while True:
            time.sleep(0.5)

    except ServiceExit:
        # update_thread.shutdown_flag.set()
        # sync_thread.shutdown_flag.set()
        # opn_sync_thread.shutdown_flag.set()

        # Tell UpdateThread to stop, which will stop all the other threads
        mq_context = zmq.Context()
        mq_socket = mq_context.socket(zmq.REQ)
        mq_socket.connect("tcp://%s:%s" % (server_config.mq_ip, server_config.mq_port))
        mq_socket.send_string("stop")
        response_msg = mq_socket.recv_string()
        mq_socket.close()
        mq_context.term()
        if response_msg == "stopped":
            logger.debug("syncfail2ban: UpdateThread confirmed stop")
        else:
            logger.debug("syncfail2ban: Failed to stop UpdateThread")

        update_thread.join()
        sync_thread.join()
        opn_sync_thread.join()


if __name__ == '__main__':
    main()
