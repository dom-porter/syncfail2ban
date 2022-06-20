all: syncfail2ban syncfail2band.service
.PHONY: all syncfail2ban install uninstall clean

service_dir=/etc/systemd/system
awk_script='BEGIN {FS="="; OFS="="}{if ($$1=="ExecStart") {$$2=exec_path} if (substr($$1,1,1) != "\#") {print $$0}}'

syncfail2ban: src/syncfail2ban/syncfail2ban.py setup.py
	pip install .
	pip install requests~=2.25.1
	pip install pyzmq~=22.3.0
	pip install configparser~=5.2.0

syncfail2band.service: src/syncfail2ban/syncfail2ban.py
# awk is needed to replace the absolute path of mydaemon executable in the .service file
	awk -v exec_path=$(/etc/syncfail2ban/syncfail2ban) $(awk_script) syncfail2band.service.template > syncfail2band.service

install: $(service_dir) $(conf_dir) syncfail2band.service
	cp syncfail2band.service $(service_dir)
	cp /usr/local/bin/syncfail2ban /etc/syncfail2ban
	cp src/syncfail2ban/data/config.cfg /etc/syncfail2ban

uninstall:
	-systemctl stop syncfail2band
	-rm -r $(service_dir)/syncfail2band.service
	-rm -r /etc/syncfail2ban

clean:
	-rm syncfail2band.service
	-rm -r /etc/syncfail2ban