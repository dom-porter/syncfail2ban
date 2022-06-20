all: syncfail2ban syncfail2ban.service
.PHONY: all syncfail2ban install uninstall clean

service_dir=/etc/systemd/system
awk_script='BEGIN {FS="="; OFS="="}{if ($$1=="ExecStart") {$$2=exec_path} if (substr($$1,1,1) != "\#") {print $$0}}'

syncfail2ban: src/syncfail2ban/syncfail2ban.py setup.py
	pip install .
	pip install requests~=2.25.1
	pip install pyzmq~=22.3.0
	pip install configparser~=5.2.0

syncfail2ban.service: src/syncfail2ban/syncfail2ban.py

install: $(service_dir) $(conf_dir) syncfail2ban.service
	cp syncfail2ban.service $(service_dir)
	cp /usr/local/bin/syncfail2ban /etc/syncfail2ban
	cp src/syncfail2ban/data/config.cfg /etc/syncfail2ban

uninstall:
	-systemctl stop syncfail2ban
	-rm -r $(service_dir)/syncfail2ban.service
	-rm -r /etc/syncfail2ban

clean:
	-rm syncfail2ban.service
	-rm -r /etc/syncfail2ban