all: syncfail2ban syncfail2ban.service
.PHONY: all syncfail2ban install uninstall clean

service_dir=/etc/systemd/system

syncfail2ban: syncfail2ban/__init__.py setup.py
	pip install .

syncfail2ban.service: syncfail2ban/__init__.py

install: $(service_dir) $(conf_dir) syncfail2ban.service
	cp syncfail2ban/data/syncfail2ban.service $(service_dir)
	mkdir /etc/syncfail2ban
	mv /usr/local/bin/syncfail2ban /etc/syncfail2ban
	mv /usr/local/bin/syncfail2ban-client /etc/syncfail2ban
	cp syncfail2ban/data/config.cfg /etc/syncfail2ban
	systemctl daemon-reload
	systemctl enable syncfail2ban

uninstall:
	systemctl stop syncfail2ban
	systemctl disable syncfail2ban
	rm -r $(service_dir)/syncfail2ban.service
	rm -r /etc/syncfail2ban
	systemctl daemon-reload
	pip uninstall syncfail2ban

clean:
    systemctl disable syncfail2ban
	rm syncfail2ban.service
	rm -r /etc/syncfail2ban
	systemctl daemon-reload
	pip uninstall syncfail2ban