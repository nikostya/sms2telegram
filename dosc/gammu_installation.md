1. Insert USB Modem in USB-port
2. Check If device was recognize
```
lsusb
```
4. Device list
```
ls -l /dev/ttyUSB* /dev/serial/by-id/*
```
6. Install modem manager
```
sudo apt update
sudo apt install usb-modeswitch
sudo apt install modemmanager
```
5. Check
```
mmcli -L
mmcli -m any
```
6. Lookup a usb port number (usb1)
```
System   |            device: /sys/devices/pci0000:00/0000:00:14.0/usb1/1-13
```
7. Check and get path to usb-port. Therefore insert it in gammu-config 
```
ls -l /dev/ttyUSB* /dev/serial/by-id/*
```
8. Install gammu
```
sudo apt install gammu gammu-smsd
```
9. Add gammu user to dialup group
```
sudo usermod -aG dialout gammu
```
10. Edit gammu config
```
sudo nano /etc/gammu-smsdrc
```
```
[gammu]
port = /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
connection = at

[smsd]
service = files
modemtype = phone
inboxformat = detail
combine = yes

# logging
logfile = /var/log/gammu-smsd.log
debuglevel = 1

inboxpath = /var/spool/gammu/inbox/
outboxpath = /var/spool/gammu/outbox/
sentsmspath = /var/spool/gammu/sent/
errorsmspath = /var/spool/gammu/error
```
11. smsd have to start uder gammu user, not root. Otherwise we couldn't read files with smss. Create config:
```
sudo nano /etc/systemd/system/gammu-smsd.service
```
config:
```
[Unit]
Description=Gammu SMS Daemon
After=network.target

[Service]
Type=simple
User=gammu
Group=gammu
ExecStart=/usr/bin/gammu-smsd -c /etc/gammu-smsdrc
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
12. Service start
```
sudo systemctl daemon-reload
sudo systemctl enable gammu-smsd
sudo systemctl start gammu-smsd
sudo systemctl status gammu-smsd
```
13. Create a rule to auto recognise of modem in case of system reboot
```
sudo nano /etc/udev/rules.d/40-huawei-e220.rules
```
Check id product from lsusb command and inset this id in string:
```
# Huawei E220 / E230 / E270 automatic mode switch
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="12d1", ATTR{idProduct}=="1003", RUN+="/usr/sbin/usb_modeswitch -v 12d1 -p 1003 -J"
```
14. Reload rules
```
sudo udevadm control --reload-rules
sudo udevadm trigger
```
15. If you eject and insert modem, you have to restart gammu service
```
sudo systemctl restart gammu-smsd
```

