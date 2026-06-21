# Bot deployment

This guide describes how to deploy the Python SMS forwarding service on a Linux server.

Before starting this guide, the GSM modem and Gammu SMSD must already be configured. Incoming SMS messages should appear as files in the Gammu inbox directory.

See [Gammu installation](gammu_installation.md) first.

## Requirements

- Linux server with systemd
- Working Gammu SMSD installation
- Incoming SMS files appearing in `/var/spool/gammu/inbox/`
- Python 3
- Git
- Nextcloud server with Talk application
- Nextcloud account with an application password
- Nextcloud Talk conversation token

## 1. Verify that Gammu receives SMS messages

Before deploying the bot, make sure that Gammu SMSD is already working.

Send a test SMS to the SIM card installed in the modem.

Check the Gammu inbox directory:

```bash
ls -la /var/spool/gammu/inbox/
```

If Gammu is configured correctly, a new SMS file should appear in this directory.

The bot will monitor this directory and process incoming `*.txt` files.

## 2. Install system packages

Update the package list:

```bash
sudo apt update
```

Install Python, virtual environment support, and Git:

```bash
sudo apt install python3 python3-venv git
```

## 3. Clone the repository

Go to the user's home directory:

```bash
cd ~
```

Clone the repository:

```bash
git clone https://github.com/nikostya/sms2telegram.git
```

Enter the project directory:

```bash
cd sms2telegram
```

The examples below assume that the project is located in:

```text
/home/<linux-user>/sms2telegram
```

Replace `<linux-user>` with the actual Linux username.

## 4. Create a Python virtual environment

Create a virtual environment inside the project directory:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

## 5. Install Python dependencies

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

The required packages are:

```text
requests
python-dotenv
```

If dependency installation fails, check that `requirements.txt` contains one package per line, for example:

```text
requests==2.32.5
python-dotenv==1.2.2
```

## 6. Create the configuration file

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Open it:

```bash
nano .env
```

Configure the required values:

```dotenv
INBOX_FOLDER=/var/spool/gammu/inbox/
NEXTCLOUD_URL=https://cloud.example.com
NC_USERNAME=nextcloud-user
NC_APP_PASSWORD=replace-with-app-password
TALK_TOKEN=replace-with-talk-token
```

### Configuration variables

| Variable | Description |
|---|---|
| `INBOX_FOLDER` | Directory where Gammu SMSD stores incoming SMS files |
| `NEXTCLOUD_URL` | Base URL of the Nextcloud server |
| `NC_USERNAME` | Nextcloud account used to send messages |
| `NC_APP_PASSWORD` | Nextcloud application password |
| `TALK_TOKEN` | Nextcloud Talk conversation token |

`NEXTCLOUD_URL` should be specified without a trailing slash.

Example:

```dotenv
NEXTCLOUD_URL=https://cloud.example.com
```

not:

```dotenv
NEXTCLOUD_URL=https://cloud.example.com/
```

## 7. Allow the bot to access Gammu SMS files

The bot must be able to:

- read files in the Gammu inbox directory;
- rename processed files by adding the `.sent` suffix.

Add the current Linux user to the `gammu` group:

```bash
sudo usermod -aG gammu "$USER"
```

Apply the new group membership for the current terminal session:

```bash
newgrp gammu
```

Make sure the Gammu inbox directory belongs to the `gammu` group and is writable by that group:

```bash
sudo chown -R gammu:gammu /var/spool/gammu
sudo chmod 2770 /var/spool/gammu/inbox
```

Check the directory permissions:

```bash
ls -ld /var/spool/gammu/inbox
```

Expected result should look similar to this:

```text
drwxrws--- 2 gammu gammu ... /var/spool/gammu/inbox
```

The `s` flag in the group permissions means that new files created inside the directory inherit the `gammu` group.

## 8. Test the bot manually

Run the bot manually from the project directory:

```bash
./venv/bin/python smstgbot.py
```

If the configuration is correct, the application should start monitoring the Gammu inbox directory.

Send a test SMS to the modem.

Expected result:

1. the SMS appears in the terminal output;
2. the message is sent to the configured Nextcloud Talk conversation;
3. the processed SMS file is renamed with the `.sent` suffix.

Stop the manual test with:

```text
Ctrl+C
```

Check the inbox directory:

```bash
ls -la /var/spool/gammu/inbox/
```

A processed file should look similar to this:

```text
IN20260621_120000_00.txt.sent
```

## 9. Create a systemd service

Create a systemd unit file:

```bash
sudo nano /etc/systemd/system/smstgbot.service
```

Add the following configuration.

Replace `<linux-user>` with the actual Linux username:

```ini
[Unit]
Description=SMS forwarding service
After=network-online.target gammu-smsd.service
Wants=network-online.target
Requires=gammu-smsd.service

[Service]
Type=simple
User=<linux-user>
WorkingDirectory=/home/<linux-user>/sms2telegram
ExecStart=/home/<linux-user>/sms2telegram/venv/bin/python /home/<linux-user>/sms2telegram/smstgbot.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

The application reads its configuration from `.env` in the project directory. This works because `WorkingDirectory` points to the project directory.

## 10. Enable and start the service

Reload systemd configuration:

```bash
sudo systemctl daemon-reload
```

Enable automatic startup:

```bash
sudo systemctl enable smstgbot.service
```

Start the service:

```bash
sudo systemctl start smstgbot.service
```

Check the service status:

```bash
sudo systemctl status smstgbot.service
```

## 11. View service logs

Follow the service log:

```bash
sudo journalctl -u smstgbot.service -f
```

Check recent log entries:

```bash
sudo journalctl -u smstgbot.service -n 100 --no-pager
```

Check logs since the last system boot:

```bash
sudo journalctl -u smstgbot.service -b --no-pager
```

## 12. Restart or stop the service

Restart the service:

```bash
sudo systemctl restart smstgbot.service
```

Stop the service:

```bash
sudo systemctl stop smstgbot.service
```

Start it again:

```bash
sudo systemctl start smstgbot.service
```

## 13. Update the application

Go to the project directory:

```bash
cd ~/sms2telegram
```

Pull the latest version from GitHub:

```bash
git pull
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Update dependencies:

```bash
pip install -r requirements.txt
```

Restart the service:

```bash
sudo systemctl restart smstgbot.service
```

Check the status:

```bash
sudo systemctl status smstgbot.service
```

## 14. Troubleshooting

### The service does not start

Check the service status:

```bash
sudo systemctl status smstgbot.service
```

View detailed logs:

```bash
sudo journalctl -u smstgbot.service -n 100 --no-pager
```

Check that the paths in the unit file are correct:

```bash
sudo systemctl cat smstgbot.service
```

Verify that the Python interpreter exists:

```bash
ls -l ~/sms2telegram/venv/bin/python
```

Verify that the script exists:

```bash
ls -l ~/sms2telegram/smstgbot.py
```

### The bot cannot find the `.env` file

Make sure the service has the correct working directory:

```bash
sudo systemctl cat smstgbot.service
```

The unit file should contain:

```ini
WorkingDirectory=/home/<linux-user>/sms2telegram
```

Check that `.env` exists in the project directory:

```bash
ls -la ~/sms2telegram/.env
```

### The bot cannot read SMS files

Check the inbox directory:

```bash
ls -ld /var/spool/gammu/inbox
ls -la /var/spool/gammu/inbox
```

Check the user running the bot:

```bash
sudo systemctl cat smstgbot.service
```

Check that this user belongs to the `gammu` group:

```bash
id <linux-user>
```

If necessary, add the user to the group:

```bash
sudo usermod -aG gammu <linux-user>
```

Then restart the service:

```bash
sudo systemctl restart smstgbot.service
```

### The bot reads SMS but cannot rename files

The bot marks processed SMS files by renaming them with the `.sent` suffix.

If renaming fails, check that the service user has write permission in the inbox directory:

```bash
ls -ld /var/spool/gammu/inbox
```

Set group ownership and permissions again:

```bash
sudo chown -R gammu:gammu /var/spool/gammu
sudo chmod 2770 /var/spool/gammu/inbox
```

Restart the service:

```bash
sudo systemctl restart smstgbot.service
```

### Messages are not delivered to Nextcloud Talk

Check the service log:

```bash
sudo journalctl -u smstgbot.service -n 100 --no-pager
```

Verify the values in `.env`:

```bash
nano ~/sms2telegram/.env
```

Check:

- `NEXTCLOUD_URL`
- `NC_USERNAME`
- `NC_APP_PASSWORD`
- `TALK_TOKEN`

Make sure that the Nextcloud account can access the target Talk conversation.

### SMS files are marked as `.sent`

A `.sent` suffix means that the file was processed by the application.

It does not necessarily guarantee successful delivery to Nextcloud Talk. Check the service logs to confirm that the HTTP request to Nextcloud Talk was successful.


Then restart the service:

```bash
sudo systemctl restart smstgbot.service
```
