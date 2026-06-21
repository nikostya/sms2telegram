# GSM modem and Gammu installation

This guide describes how to connect a USB GSM modem, configure Gammu SMSD, and verify that incoming SMS messages are saved as files.

The examples below were tested with a Huawei USB modem on a Debian/Ubuntu-based Linux system. Device names, USB identifiers, modem modes, and serial ports may differ for other hardware.

## Modem compatibility

Not every USB modem is suitable for this project.

The modem must provide a serial interface that can be accessed by Gammu and must support the AT commands required for SMS operations.

On Linux, a compatible modem usually appears as one or more serial devices, for example:

```text
/dev/ttyUSB0
/dev/ttyUSB1
/dev/ttyACM0
```

Some modems expose several serial ports. Only one of them may support modem control and SMS operations, so the correct port must be identified during configuration.

USB modems that operate only as network adapters, use a web-based management interface, or do not expose an AT-compatible serial port may not work with Gammu.

Before purchasing or configuring a modem, check:

- whether it supports AT commands;
- whether it exposes a serial port under Linux;
- whether SMS sending and receiving are supported through that port;
- whether the model is listed in the [Gammu Phone Database](https://wammu.eu/phones/).

Compatibility can also depend on the modem firmware and operating mode. Some modems may require `usb-modeswitch` before their serial ports become available.

## Requirements

- Debian, Ubuntu, Armbian, or another Debian-based Linux system
- USB GSM modem with an AT-compatible serial interface and SMS support
- SIM card capable of receiving SMS messages
- Administrative access through `sudo`

## 1. Connect the modem

Insert the GSM modem into a USB port.

Check that the system detects it:

```bash
lsusb
```

The modem should appear in the list of connected USB devices.

## 2. Check modem device files

Check whether serial modem devices were created:

```bash
ls -l /dev/ttyUSB*
```

Some modems may appear as `/dev/ttyACM*` devices instead:

```bash
ls -l /dev/ttyACM*
```

Also check for persistent device names:

```bash
ls -l /dev/serial/by-id/
```

A path under `/dev/serial/by-id/` is preferable because it normally remains stable after a reboot or after reconnecting the modem.

Example:

```text
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
```

The actual path on your system may be different.

## 3. Install modem utilities

Update the package list:

```bash
sudo apt update
```

Install `usb-modeswitch`:

```bash
sudo apt install usb-modeswitch
```

Some USB modems initially appear as storage devices and must be switched into modem mode. `usb-modeswitch` performs this conversion.

For optional modem diagnostics, install ModemManager:

```bash
sudo apt install modemmanager
```

Check whether ModemManager detects the modem:

```bash
mmcli -L
```

Display detailed modem information:

```bash
mmcli -m any
```

ModemManager is not required for Gammu operation.

If it keeps the serial port busy and prevents Gammu from accessing the modem, stop it before continuing:

```bash
sudo systemctl stop ModemManager
```

## 4. Install Gammu

Install Gammu and Gammu SMSD:

```bash
sudo apt install gammu gammu-smsd
```

Gammu provides access to the GSM modem. Gammu SMSD periodically checks the modem for incoming messages and stores them using the configured backend.

## 5. Test AT communication

Before configuring Gammu SMSD, verify that Gammu can communicate with the modem.

Test the first detected serial port:

```bash
sudo gammu --device /dev/ttyUSB0 --connection at identify
```

Replace `/dev/ttyUSB0` with the serial device detected on your system.

If the port is correct, Gammu should display information such as:

- modem manufacturer;
- modem model;
- firmware version;
- IMEI.

If the modem exposes several serial ports, test them one by one until Gammu successfully identifies the modem.

For example:

```bash
sudo gammu --device /dev/ttyUSB1 --connection at identify
```

or:

```bash
sudo gammu --device /dev/ttyUSB2 --connection at identify
```

A successful `gammu identify` command confirms that:

- the serial port is accessible;
- the modem accepts AT commands;
- Gammu can communicate with the device.

## 6. Add the Gammu user to the dialout group

Add the `gammu` system user to the `dialout` group so that it can access serial devices:

```bash
sudo usermod -aG dialout gammu
```

The Gammu SMSD service must be restarted after this change so that the new group membership takes effect.

## 7. Configure Gammu SMSD

Open the Gammu SMSD configuration file:

```bash
sudo nano /etc/gammu-smsdrc
```

Use the following configuration as a template:

```ini
[gammu]
port = /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
connection = at

[smsd]
service = files
modemtype = phone

inboxformat = detail
combine = yes

logfile = /var/log/gammu-smsd.log
debuglevel = 1

inboxpath = /var/spool/gammu/inbox/
outboxpath = /var/spool/gammu/outbox/
sentsmspath = /var/spool/gammu/sent/
errorsmspath = /var/spool/gammu/error/
```

Replace the value of `port` with the persistent device path detected on your system:

```bash
ls -l /dev/serial/by-id/
```

If no persistent path is available, a serial device such as `/dev/ttyUSB0` can be used instead. However, its number may change after a reboot or after reconnecting the modem.

The configuration uses the Gammu `files` backend. Incoming SMS messages are written to the directory specified by `inboxpath`.

If the SIM card requires a PIN, add it to the `[smsd]` section:

```ini
PIN = 1234
```

Replace `1234` with the actual SIM PIN.

## 8. Create SMS directories

Create the directories configured in `/etc/gammu-smsdrc`:

```bash
sudo mkdir -p \
    /var/spool/gammu/inbox \
    /var/spool/gammu/outbox \
    /var/spool/gammu/sent \
    /var/spool/gammu/error
```

Assign them to the `gammu` user:

```bash
sudo chown -R gammu:gammu /var/spool/gammu
```

## 9. Configure the systemd service

Create or replace the systemd unit:

```bash
sudo nano /etc/systemd/system/gammu-smsd.service
```

Add the following configuration:

```ini
[Unit]
Description=Gammu SMS Daemon
After=network.target

[Service]
Type=simple
User=gammu
Group=gammu
ExecStart=/usr/bin/gammu-smsd -c /etc/gammu-smsdrc
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

This configuration runs Gammu SMSD as the `gammu` user instead of `root`.

Reload systemd after creating or modifying the unit:

```bash
sudo systemctl daemon-reload
```

Enable automatic startup:

```bash
sudo systemctl enable gammu-smsd.service
```

Start the service:

```bash
sudo systemctl start gammu-smsd.service
```

Check its status:

```bash
sudo systemctl status gammu-smsd.service
```

## 10. View Gammu logs

Follow the systemd journal:

```bash
sudo journalctl -u gammu-smsd.service -f
```

You can also inspect the log file configured in `/etc/gammu-smsdrc`:

```bash
sudo tail -f /var/log/gammu-smsd.log
```

## 11. Test incoming SMS reception

Send an SMS message to the SIM card installed in the modem.

Check the inbox directory:

```bash
ls -la /var/spool/gammu/inbox/
```

If the configuration is working, Gammu SMSD should create a new file containing the received message.

Display the contents of received message files:

```bash
sudo cat /var/spool/gammu/inbox/*
```

At this point, the GSM modem and Gammu SMSD configuration is complete.

The Python application can now monitor `/var/spool/gammu/inbox/` and forward received messages to Nextcloud Talk.

## Huawei modem mode switching

Some Huawei modems may return to storage-device mode after a reboot or reconnect. In that case, create a udev rule that automatically runs `usb_modeswitch`.

First, identify the USB vendor and product IDs:

```bash
lsusb
```

Example output:

```text
Bus 001 Device 004: ID 12d1:1003 Huawei Technologies Co., Ltd.
```

In this example:

- Vendor ID: `12d1`
- Product ID: `1003`

Create a udev rule:

```bash
sudo nano /etc/udev/rules.d/40-huawei-e220.rules
```

Add the following rule:

```udev
# Huawei E220 / E230 / E270 automatic mode switch
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="12d1", ATTR{idProduct}=="1003", RUN+="/usr/sbin/usb_modeswitch -v 12d1 -p 1003 -J"
```

Replace the vendor and product IDs with the values reported by `lsusb` for your modem.

Reload the udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Disconnect and reconnect the modem, then verify that the serial devices appear:

```bash
ls -l /dev/ttyUSB*
ls -l /dev/serial/by-id/
```

Restart Gammu SMSD after reconnecting the modem:

```bash
sudo systemctl restart gammu-smsd.service
```

## Troubleshooting

### No serial modem devices appear

Check recent kernel messages:

```bash
sudo dmesg | tail -50
```

Verify that the modem appears in the USB device list:

```bash
lsusb
```

Check for both common serial device types:

```bash
ls -l /dev/ttyUSB*
ls -l /dev/ttyACM*
```

The modem may still be operating in storage-device mode. Check the `usb-modeswitch` configuration and, for Huawei modems, the udev rule.

### Gammu cannot identify the modem

Try each serial port exposed by the modem:

```bash
sudo gammu --device /dev/ttyUSB0 --connection at identify
sudo gammu --device /dev/ttyUSB1 --connection at identify
sudo gammu --device /dev/ttyUSB2 --connection at identify
```

Check whether ModemManager or another application is using the port:

```bash
sudo lsof /dev/ttyUSB0
```

If ModemManager is using it, stop the service:

```bash
sudo systemctl stop ModemManager
```

Then repeat the identification test.

### Gammu SMSD cannot open the modem port

Check ownership and permissions:

```bash
ls -l /dev/ttyUSB*
```

Verify that the `gammu` user belongs to the `dialout` group:

```bash
id gammu
```

Check whether another process is using the configured serial port:

```bash
sudo lsof /dev/ttyUSB0
```

If ModemManager is using the port, stop it:

```bash
sudo systemctl stop ModemManager
```

Then restart Gammu SMSD:

```bash
sudo systemctl restart gammu-smsd.service
```

### The service does not start

Check its status:

```bash
sudo systemctl status gammu-smsd.service
```

View detailed log messages:

```bash
sudo journalctl -u gammu-smsd.service -n 100 --no-pager
```

Verify that the configured modem path exists:

```bash
ls -l /dev/serial/by-id/
```

Also verify that the configuration file contains the correct port:

```bash
grep -E '^[[:space:]]*port[[:space:]]*=' /etc/gammu-smsdrc
```

### The modem was disconnected and reconnected

Verify that the modem device path is still available:

```bash
ls -l /dev/serial/by-id/
```

Restart the service:

```bash
sudo systemctl restart gammu-smsd.service
```

Then check its status:

```bash
sudo systemctl status gammu-smsd.service
```
