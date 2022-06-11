import configparser


# wrapper class for the config file
class SyncConfig(object):

    def __init__(self, path):
        self.config = configparser.ConfigParser()
        self.config.read(path)

    def getmq_port(self):
        return self.config.get('default','mq_port')

    def getsync_servers(self):
        return self.config.get('default','sync_servers')

    def getmq_ip(self):
        return self.config.get('default', 'mq_ip')
    
    def gettimeout(self):
        return self.config.get('default', 'connection_timeout')

    def getjail_names(self):
        return dict(self.config['jails'])


# Searches srtString from right to left for strPattern and returns a substring
# containing the chars in the string that follow the pattern
def strRightBack(str_string, str_pattern):
    str_reversed = str_string[::-1]
    str_reversed_pattern = str_pattern[::-1]
    end = str_reversed.find(str_reversed_pattern)
    str_return = str_reversed[0:end]
    return str_return[::-1]


class SyncList(object):

    def __init__(self, max_length_):
        self.max_length = max_length_ -1
        self.sync_list = []

    def add_ip(self, ip_address_):
        if len(self.sync_list) == self.max_length:
            self.sync_list.pop(0)
        else:
            self.sync_list.append(ip_address_)

    def is_member(self, ip_address_):
        target = ip_address_.strip()
        for member in self.sync_list:
            if member == target:
                return "1"
        return "0"


# Constants
CONFIG_FILENAME = "config.cfg"

