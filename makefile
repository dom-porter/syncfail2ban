all: syncfail2ban syncfail2ban.service
.PHONY: all syncfail2ban install uninstall clean

service_dir=/etc/systemd/system

syncfail2ban: syncfail2ban/__init__.py setup.py
	pip install .

syncfail2ban.service: syncfail2ban/__init__.py

install: $(service_dir) $(conf_dir) syncfail2ban.service
	cp syncfail2ban/data/syncfail2ban.service $(service_dir)
	mkdir /etc/syncfail2ban
	cp /usr/local/bin/syncfail2ban /etc/syncfail2ban
	cp syncfail2ban/data/config.cfg /etc/syncfail2ban
	systemctl daemon-reload
	systemctl enable syncfail2ban

uninstall:
	systemctl stop syncfail2ban || true
	systemctl disable syncfail2ban || true
	rm -r $(service_dir)/syncfail2ban.service || true
	systemctl daemon-reload || true
	rm /etc/syncfail2ban/syncfail2ban || true
    rm /etc/syncfail2ban/syncfail2ban-client || true
    pip uninstall syncfail2ban

clean:
	systemctl disable syncfail2ban || true
	rm syncfail2ban.service || true
	rm -r /etc/syncfail2ban || true
	systemctl daemon-reload || true
    pip uninstall syncfail2ban
