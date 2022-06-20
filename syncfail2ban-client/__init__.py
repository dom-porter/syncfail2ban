import zmq
import logging
import pathlib
import sys
import subprocess
import signal
from syncfail2ban.syncfail2ban.SyncConfig import SyncConfig

# Constants
CONFIG_FILENAME = "config.cfg"


def sigint_handler(sig, frame):
    sys.exit(0)


def send_message(message, ip_target, server_config):
    mq_context = None
    mq_socket = None

    try:
        mq_context = zmq.Context()
        mq_socket = mq_context.socket(zmq.REQ)
        mq_socket.setsockopt(zmq.LINGER, 0)

        mq_socket.connect("tcp://%s:%s" % (ip_target, server_config.mq_port))

        mq_socket.send_string(message)
        poller = zmq.Poller()
        poller.register(mq_socket, zmq.POLLIN)

        # if there is no response from the target host raise an error
        if poller.poll(int(server_config.timeout) * 1000):
            response_msg = mq_socket.recv_string()

            # Just for testing so it will shutdown the server
            # mq_socket.send_string("stop")
            # response_msg = mq_socket.recv_string()

            return response_msg
        else:
            raise IOError("Timeout connecting to server {0}:{1}"
                          .format(ip_target, server_config.mq_port))

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


# Searches srtString from right to left for strPattern and returns a substring
# containing the chars in the string that follow the pattern
def str_rightback(str_string, str_pattern):
    str_reversed = str_string[::-1]
    str_reversed_pattern = str_pattern[::-1]
    end = str_reversed.find(str_reversed_pattern)
    str_return = str_reversed[0:end]
    return str_return[::-1]


def main():
    logging.basicConfig(filename="/var/log/syncfail2ban.log", level=logging.INFO, format="%(asctime)s-%(message)s")
    server_config = SyncConfig(pathlib.Path(__file__).parent.absolute().__str__() + "/" + CONFIG_FILENAME)

    sync_type = 0
    list_sync_targets = ""
    ban_action = ""
    ip_address = ""
    local_server = server_config.mq_ip
    message = ""

    try:
        # Used to perform a full sync of a jail
        if str(sys.argv[1]).lower() == "-f":
            sync_type = 2
            jail_name = str(sys.argv[2])

        # Used to sync a single ip to ban or unban
        elif str(sys.argv[1]).lower() == "-s":
            sync_type = 1
            jail_name = str(sys.argv[2])
            ban_action = str(sys.argv[3])
            ip_address = str(sys.argv[4])

        # Used from the fail2ban action
        elif str(sys.argv[1]).lower() == "-a":
            sync_type = 3
            jail_name = str(sys.argv[2])
            ban_action = str(sys.argv[3])
            ip_address = str(sys.argv[4])

        else:
            print("Incorrect launch option used")
            raise ValueError("Incorrect launch option used")

    except ValueError as e_val:
        print("Error: {0} ({1})".format(e_val, str(sys.argv[1])))
        raise SystemExit

    if sync_type == 2:
        # Full sync of jail_name with list_sync_targets (it's a single target though)
        try:
            # This is a bit shit.  Access the sqlite3 database directly later
            ban_list = subprocess.run(['fail2ban-client', 'status', jail_name],
                                      check=True, capture_output=True, text=True)
            ban_list = str_rightback(ban_list.stdout.__str__().lower(), "ip list:").strip()

            ban_list = ban_list.split()

            for ban_ip in ban_list:
                message = "{0} banip {1}".format(jail_name, ban_ip)
                response = send_message(message, local_server, server_config)

                if response == "1":
                    print("{0} - sent to local sync server".format(message))
                else:
                    print("{0} - not sent to local sync server".format(message))

                # check if the network connection had an error and stop further connections if it did
                if response == "99":
                    break

        except subprocess.CalledProcessError as pe:
            print("Error: unable to extract ban list from fail2ban - {0}"
                  .format(str_rightback(pe.stderr, "ERROR").strip()))

    elif sync_type == 1:
        # Single IP address to add to jail_name on all list_sync_targets
        message = "{0} {1} {2}".format(jail_name, ban_action, ip_address)
        response = send_message(message, local_server, server_config)

        if response == "1":
            print("{0} - sent to local sync server".format(message))
        else:
            print("{0} - not sent to local sync server".format(message))

    elif sync_type == 3:
        # Used for the action to send message to local mq_server
        # print("Syncing {0} with {1}".format(jail_name, local_server))
        message = "{0} {1} {2}".format(jail_name, ban_action, ip_address)
        response = send_message(message, local_server, server_config)


signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    main()
