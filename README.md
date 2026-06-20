0. Inatall and configure gammu service [gammu installation](docs/gammu_installation.md)

# sms2telegram
SMS 2 Telegram bot

1. Insert your Telegram-bot token and chat_id
2. Create system daemon
 
```sudo nano /etc/systemd/system/smstgbot.service```

```
[Unit]
Description=SMS-2-Telegram  Bot
After=network-online.target
Wants=network-online.target

[Service]
User=nikostya
Group=nikostya
WorkingDirectory=/home/nikostya/smstgbot

Environment="PATH=/home/nikostya/smstgbot/venv/bin:/usr/bin:/bin:/usr/local/bin"
ExecStartPre=/bin/sleep 3

ExecStart=/home/nikostya/smstgbot/venv/bin/python3 /home/nikostya/smstgbot/smstgbot.py --start
ExecStop=/home/nikostya/smstgbot/venv/bin/python3 /home/nikostya/smstgbot.py --stop
ExecReload=/home/nikostya/smstgbot/venv/bin/python3 /home/nikostya/smstgbot.py --restart

Restart=always
RestartSec=5
TimeoutSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```
Then run these commands
```
sudo systemctl daemon-reload
sudo systemctl enable smstgbot.service
sudo systemctl start smstgbot.service
```
