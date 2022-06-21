## Description
As the name suggests, the app will synchronise fail2ban jails across servers.  It will also update OPNSense aliases which can then be used to block traffic at the firewall level.

## Assumptions
You are familiar with fail2ban and already have a working system.

Python package manager PIP is installed.
## Installation

      git clone https://github.com/syncfail2ban/syncfail2ban.git
      cd syncfail2ban
      sudo make
      sudo make install

## Setup

The logic of the fail2ban jail synchronisation is that IP addresses which are banned/unbanned on other servers are updated in a sync-jail on the local server, and not the primary jail where the ban/unban action took place.

For example [Server A] --> Ban 40.67.89.7 in jail ssh --> SYNC --> [Server B] --> Ban 40.67.89.7 in jail ssh-sync

The sync-jail is configured in such a way that fail2ban will never update it during normal operation and will be managed by syncfail2ban using the fail2ban-client.

***NOTE:***
***If at any point there is no network connection between servers ban/unban actions will not be sent to other servers and will not be sent when the connection is restored.*** 

* **Update Configuration**

      sudo nano /etc/syncfail2ban/config.cfg
  
      -- Minimal Config --

      f2b_sync = true
      mq_port = 18862
      mq_ip = <LOCAL_SERVER_IP>
      sync_servers = <SERVER_IP>
      connection_timeout = 10

      [jails]
      <PRIMARY-JAIL-NAME> = <SYNC-JAIL-NAME>

* **Create Sync Action**

      sudo nano /etc/fail2ban/action.d/sync-action.cfg

      # bypass ban/unban for restored tickets and flush
      norestored = 1
      actionflush = true

      actionban = /etc/syncfail2ban/syncfail2ban-client -a <name> banip <ip>
      actionunban = /etc/syncfail2ban/syncfail2ban-client -a <name> unbanip <ip>

* **Create Dummy Log**

       sudo touch /var/log/dummy.log

* **Create Dummy Filter**

       sudo nano /etc/fail2ban/filter.d/sync-filter.conf 

       [Definition]
       failregex = (?<![\w\d])connect(?![\w\d]) fail2ban sync dummy filter\[<HOST>\]
       ignoreregex =

* **Update Jail Configuration**

  For each jail you wish to synchronise add sync-action under action, then create a sync-jail config.

  Don't forget to make sure that the /etc/syncfail2ban/config.cfg [jails] section is correct.

        sudo nano /etc/fail2ban/jail.local

        [postfix]
        enabled = true
        port = smtp,ssmtp,submission
        filter = postfix
        logpath = /var/log/mail.log
        action = iptables-allports
                 sync-action
        findtime  = 3d
        maxretry = 1
        bantime  = 30d
        ignoreip = 127.0.0.1/8 192.168.10.0/24


        # Note - make sure that the bantime = -1
        [postfix-sync]
        enabled = true
        filter = sync-filter
        logpath = /var/log/dummy.log
        action = iptables-allports
        findtime  = 3d
        maxretry = 1
        bantime  = -1
        ignoreip = 127.0.0.1/8 192.168.10.0/24

* **Start the Server**

       sudo service syncfail2ban start

## syncfail2ban-client

The syncfail2ban-client app is used by the action to send information about the ban/unban action to the syncfail2ban server. It will NOT update the local fail2ban jail. It can also be used manually:
    
    To send a single action to all other servers:
    syncfail2ban -a <JAIL-NAME> <BAN_ACTION> <BAD-IP-ADDRES>

    Example:
    sudo /etc/syncfail2ban/syncfail2ban-client -a postfix banip 19.76.34.123


    To send all contents of a jail to all other servers:
    syncfail2ban -f <JAIL-NAME>

    Example:
    sudo /etc/syncfail2ban/syncfail2ban-client -a postfix

## License
Apache License Version 2.0

