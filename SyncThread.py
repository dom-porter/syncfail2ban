import logging
import zmq
from queue import Queue
from threading import Thread
from common import SyncConfig

logger = logging.getLogger(__name__)


# Sync the IPs to the target servers
class SyncThread(Thread):
    def __init__(self, server_config: SyncConfig, work_queue: Queue):
        Thread.__init__(self)
        self._server_config = server_config
        self._work_queue = work_queue

    def run(self):
        logger.debug("SyncThread - Started")
        sync_is_continue = True

        while sync_is_continue:
            message = self._work_queue.get()
            if message == "stop":
                self._work_queue.task_done()
                sync_is_continue = False

            else:
                # sync message to all sync targets

                for ip_target in self._server_config.sync_servers.split():
                    logger.info("Sync Processing - {0} with {1}".format(message, ip_target))

                    response = sync_message(ip_target, message, self._server_config.mq_port,
                                            self._server_config.timeout)
                    if response == "1":
                        logger.info("[{0}] Updated fail2ban - {1}".format(ip_target, message))
                    else:
                        logger.info("[{0}] Failed to update fail2ban - {1}".format(ip_target, message))

                self._work_queue.task_done()


def sync_message(ip_target_, message_, mq_port_, timeout_):
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
        logger.error(
            "Sync failure, unable to connect to server {0}:{1} - {2}".format(ip_target_, mq_port_, e_io))
        mq_socket.close()
        mq_context.term()

    except zmq.ZMQError as e_zmq:
        logger.error(
            "Sync failure, unable to connect to server {0}:{1} - {2}".format(ip_target_, mq_port_, e_zmq))
        mq_socket.close()
        mq_context.term()