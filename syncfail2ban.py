import pathlib
import logging
from UpdateThread import UpdateThread
from SyncThread import SyncThread
from SyncOPNThread import SyncOPNThread
from common import SyncConfig
from queue import Queue

# Constants
CONFIG_FILENAME = "config.cfg"
VERSION = "1.2 17062022"

logging.basicConfig(filename="/var/log/syncfail2ban.log",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


def main():

    server_config = SyncConfig(pathlib.Path(__file__).parent.absolute().__str__() + "/" + CONFIG_FILENAME)

    logger.info(f"====================================")
    logger.info(f"     syncfail2ban v{VERSION}")
    logger.info(f"====================================")

    mq_ip_address = server_config.mq_ip
    mq_port = server_config.mq_port
    sync_jails = server_config.jail_names
    mq_timeout = server_config.timeout
    sync_targets = server_config.sync_servers

    work_queue = Queue()
    opn_work_queue = Queue()

    update_thread = UpdateThread(server_config, work_queue, opn_work_queue)
    sync_thread = SyncThread(server_config, work_queue)
    opn_sync_thread = SyncOPNThread(server_config, opn_work_queue)

    update_thread.start()
    sync_thread.start()
    opn_sync_thread.start()
    update_thread.join()


if __name__ == '__main__':
    main()
