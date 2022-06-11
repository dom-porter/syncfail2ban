
import zmq
import logging
import pathlib
from common import *
import sys
import subprocess
import signal


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def send_message(message_, ip_target_):

    try:
        mq_context = zmq.Context()
        mq_socket = mq_context.socket(zmq.REQ)
        mq_socket.setsockopt(zmq.LINGER, 0)

        mq_socket.connect("tcp://%s:%s" % (ip_target_, server_config.getmq_port()))

        mq_socket.send_string(message_)
        poller = zmq.Poller()
        poller.register(mq_socket, zmq.POLLIN)

        # if there is no response from the target host raise an error
        if poller.poll(int(server_config.gettimeout()) * 1000):
            response_msg = mq_socket.recv_string()

            # Just for testing so it will shutdown the server
            # mq_socket.send_string("stop")
            # response_msg = mq_socket.recv_string()

            return response_msg
        else:
            raise IOError("Timeout connecting to server {0}:{1}"
                          .format(ip_target_, server_config.getmq_port()))

    except IOError as e_io:
        print("Error: Unable to connect to server - {0}".format(e_io))
        mq_socket.close()
        mq_context.term()
        return "99"

    except zmq.ZMQError as e_zmq:
        print("Error: ZMQ Unable to connect to server - {0}".format(e_zmq.strerror))
        mq_socket.close()
        mq_context.term()
        return "99"


if __name__ == '__main__':

    logging.basicConfig(filename="/var/log/syncfail2ban.log", level=logging.INFO, format="%(asctime)s-%(message)s")
    server_config = SyncConfig(pathlib.Path(__file__).parent.absolute().__str__() + "/" + CONFIG_FILENAME)

    try:
        # Arguments: -s sync single ip -f for full sync
        if str(sys.argv[1]).lower() == "-f":
            sync_type = 2
            jail_name = str(sys.argv[2])
            list_sync_targets = str(sys.argv[3])

        elif str(sys.argv[1]).lower() == "-s":
            sync_type = 1
            jail_name = str(sys.argv[2])
            ban_action = str(sys.argv[3])
            ip_address = str(sys.argv[4])
            list_sync_targets = server_config.getsync_servers()

        elif str(sys.argv[1]).lower() == "-a":
            sync_type = 3
            jail_name = str(sys.argv[2])
            ban_action = str(sys.argv[3])
            ip_address = str(sys.argv[4])
            local_server = server_config.getmq_ip()

        else:
            print("Incorrect launch option used")
            raise ValueError("Incorrect launch option used")

    except ValueError as e_val:
        print("Error: {0} ({1})".format(e_val, str(sys.argv[1])))
        raise SystemExit

    # logging.info(" Info: Syncing with server(s)...")

    if sync_type == 2:
        # Full sync of jail_name with list_sync_targets (it's a single target though)
        try:
            # This is a bit shit.  Access the sqlite3 database directly later
            ban_list = subprocess.run(['fail2ban-client', 'status', jail_name],
                                      check=True, capture_output=True, text=True)
            ban_list = strRightBack(ban_list.stdout.__str__().lower(), "ip list:").strip()

            ban_list = ban_list.split()
            print("Syncing {0} with {1}" .format(jail_name, list_sync_targets))

            for ban_ip in ban_list:
                response = send_message("{0} banip {1}".format(jail_name, ban_ip), list_sync_targets)
                if response == "1":
                    print("Add {0} to {1} - Success" .format(ban_ip, jail_name))
                else:
                    print("Add {0} to {1} - Failure".format(ban_ip, jail_name))

                # check if the network connection had an error and stop further connections if it did
                if response == "99":
                    break

        except subprocess.CalledProcessError as pe:
            print("Error: unable to extract ban list from fail2ban - {0}"
                  .format(strRightBack(pe.stderr, "ERROR").strip()))

    elif sync_type == 1:
        # Single IP address to add to jail_name on all list_sync_targets
        for ip_target in list_sync_targets.split():
            print("Syncing {0} with {1}" .format(jail_name, ip_target))
            response = send_message("{0} {1} {2}".format(jail_name, ban_action, ip_address), ip_target)

            if response == "1":
                print("Add {0} to {1} - Success".format(ip_address, jail_name))
            else:
                print("Add {0} to {1} - Failure".format(ip_address, jail_name))

    elif sync_type == 3:
        # Used for the action to send message to local mq_server
        # print("Syncing {0} with {1}".format(jail_name, local_server))
        response = send_message("{0} {1} {2}".format(jail_name, ban_action, ip_address), local_server)

        # if response == "1":
             # print("Add {0} to {1} - Success".format(ip_address, jail_name))
        # else:
             # print("Add {0} to {1} - Failure".format(ip_address, jail_name))

