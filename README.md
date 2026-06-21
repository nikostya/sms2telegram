# sms2telegram

A Python service that receives SMS messages through a GSM modem and forwards them to Nextcloud Talk.

The project was originally created for forwarding SMS messages to Telegram. The current version uses Nextcloud Talk, while Telegram integration is temporarily disabled. See the [Nextcloud Server installation documentation](https://docs.nextcloud.com/server/stable/admin_manual/installation/index.html) and the [Nextcloud Talk documentation](https://nextcloud-talk.readthedocs.io/).

## How it works

1. A GSM modem receives an SMS message.
2. Gammu SMSD saves the message as a file in the inbox directory.
3. The Python service monitors the inbox directory.
4. The service reads and decodes the SMS message.
5. The message is forwarded to a Nextcloud Talk conversation.
6. The processed SMS file is renamed with the `.sent` suffix.

## Features

- Receiving SMS messages through a GSM modem
- Integration with Gammu SMSD
- Forwarding messages to Nextcloud Talk
- Support for multipart SMS messages
- Configuration through environment variables
- Automatic startup as a systemd service
- Automatic restart after an application failure

## Requirements

- Linux server with systemd
- USB GSM modem with an AT-compatible serial interface. This project tested on Huawei E1550 modem
- SIM card capable of receiving SMS messages
- Gammu and Gammu SMSD
- Python 3
- Nextcloud server with the Talk application. See the [Nextcloud Server installation documentation](https://docs.nextcloud.com/server/stable/admin_manual/installation/index.html) and the [Nextcloud Talk documentation](https://nextcloud-talk.readthedocs.io/).
- Nextcloud account and application password
- Nextcloud Talk conversation token

## Installation

Installation consists of two stages:

1. [Configure the GSM modem and Gammu SMSD](docs/gammu_installation.md)
2. [Deploy and configure the Python service](docs/bot_deployment.md)

Application settings and credentials are stored in a local `.env` file.

The repository contains an `.env.example` file with the required configuration variables. During deployment, use it to create the local configuration file:

```bash
cp .env.example .env
```

The complete installation and configuration procedure is described in the [bot deployment guide](docs/bot_deployment.md).

## Configuration

The application uses the following environment variables:

| Variable | Description |
|---|---|
| `INBOX_FOLDER` | Directory where Gammu SMSD stores incoming SMS files |
| `NEXTCLOUD_URL` | Base URL of the Nextcloud server |
| `NC_USERNAME` | Nextcloud account used to send messages |
| `NC_APP_PASSWORD` | Nextcloud application password |
| `TALK_TOKEN` | Nextcloud Talk conversation token |

## Service management

After deployment, the application runs as a systemd service.

Check the service status:

```bash
sudo systemctl status smstgbot.service
```

Restart the service:

```bash
sudo systemctl restart smstgbot.service
```

View the service log:

```bash
sudo journalctl -u smstgbot.service -f
```

## Repository structure

```text
sms2telegram/
├── docs/
│   ├── gammu_installation.md
│   └── bot_deployment.md
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── smstgbot.py
```

## Project status

The current version forwards incoming SMS messages to Nextcloud Talk.

Telegram integration remains in the source code but is temporarily disabled.
