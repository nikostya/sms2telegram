# Version: smstgnxbot_v1.0-talk-only

import os
import glob
import asyncio
from datetime import datetime
import requests

from dotenv import load_dotenv

# Telegram временно отключён.
# Чтобы вернуть Telegram, нужно раскомментировать импорт, настройки,
# создание Bot/Dispatcher, функцию send_to_telegram(), Telegram-блок
# в watch_inbox() и dp.start_polling(bot) в main().
#
# from aiogram import Bot, Dispatcher

load_dotenv()

INBOX_FOLDER = os.getenv("INBOX_FOLDER")
#INBOX_FOLDER = "/var/spool/gammu/inbox/"

# BOT_TOKEN = "**************************"
# TELEGRAM_CHAT_ID = 123456789

NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
NC_USERNAME = os.getenv("NC_USERNAME")
NC_APP_PASSWORD = os.getenv("NC_APP_PASSWORD")
TALK_TOKEN = os.getenv("TALK_TOKEN")

# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()


def read_sms_file(file_path):
    """Читает файл Gammu и возвращает (messages, текст сообщения)."""
    messages = {}
    current_part = None

    try:
        f = open(file_path, "r", encoding="utf-8")
        lines = f.readlines()
        f.close()
    except UnicodeDecodeError:
        # Если не UTF-8 — пробуем Latin-1, чтобы не упасть.
        f = open(file_path, "r", encoding="latin-1", errors="ignore")
        lines = f.readlines()
        f.close()

    for line in lines:
        line = line.strip()
        if line.startswith("[SMSBackup"):
            current_part = line.strip("[]")
            messages[current_part] = {}
        elif "=" in line and current_part:
            key, value = line.split("=", 1)
            messages[current_part][key.strip()] = value.strip()

    # Собираем текст.
    full_text = ""
    for part_key in sorted(messages.keys()):
        part = messages[part_key]
        text_fields = [v for k, v in part.items() if k.startswith("Text")]
        for text_hex in text_fields:
            bytes_text = bytes.fromhex(text_hex)
            full_text += bytes_text.decode("utf-16-be")

    return messages, full_text


def extract_number_and_date(messages):
    """Достаёт номер и дату из первой части."""
    if not messages:
        return None, None

    first_key = sorted(messages.keys())[0]
    part = messages[first_key]

    # Номер (в Unicode).
    number_unicode = part.get("NumberUnicode")
    if number_unicode:
        number = bytes.fromhex(number_unicode).decode("utf-16-be")
    else:
        number = part.get("Number", "Неизвестен")

    # Время в формате 20251004T170223 → 04.10.25 17:02.
    date_str = part.get("DateTime", "")
    formatted_date = None
    if date_str and len(date_str) >= 15:
        try:
            dt = datetime.strptime(date_str, "%Y%m%dT%H%M%S")
            formatted_date = dt.strftime("%d.%m.%y %H:%M")
        except Exception:
            formatted_date = date_str

    return number, formatted_date


# Telegram временно отключён.
#
# async def send_to_telegram(number, date, text):
#     """Отправляет сообщение в Telegram."""
#     message = f"От: {number}\nВремя: {date}\n\n{text}"
#     await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def send_to_nextcloud_talk(number, date, text):
    """Отправляет сообщение в Nextcloud Talk."""
    message = f"От: {number}\nВремя: {date}\n\n{text}"

    url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/chat/{TALK_TOKEN}"
    headers = {
        "OCS-APIRequest": "true"
    }
    data = {
        "message": message
    }

    r = requests.post(
        url,
        auth=(NC_USERNAME, NC_APP_PASSWORD),
        headers=headers,
        data=data,
        timeout=10
    )

    if r.status_code != 201:
        print("Ошибка отправки в Nextcloud Talk:", r.status_code, r.text)


def try_mark_sent(file_path):
    """Переименовывает файл, добавляя .sent."""
    new_name = file_path + ".sent"
    try:
        os.rename(file_path, new_name)
        print(f"Переименован: {file_path} -> {new_name}")
    except Exception as e:
        print(f"Ошибка при переименовании {file_path}: {e}")


async def watch_inbox():
    print(f"Слежение за папкой {INBOX_FOLDER} запущено...")

    while True:
        for file_path in glob.glob(os.path.join(INBOX_FOLDER, "*.txt")):
            messages, text = read_sms_file(file_path)
            number, date = extract_number_and_date(messages)

            print(f"SMS от {number} ({date}):\n{text}\n{'-' * 40}")

            # Telegram временно отключён.
            #
            # try:
            #     await send_to_telegram(number, date, text)
            # except Exception as e:
            #     print("Ошибка отправки в Telegram:", e)

            # Отправляем SMS только в Nextcloud Talk.
            try:
                send_to_nextcloud_talk(number, date, text)
            except Exception as e:
                print("Ошибка отправки в Nextcloud Talk:", e)

            # Сохраняем прежнюю логику: после обработки помечаем файл как sent.
            try_mark_sent(file_path)

        await asyncio.sleep(1)


async def main():
    # Telegram polling временно отключён.
    # await asyncio.gather(
    #     watch_inbox(),
    #     dp.start_polling(bot)
    # )

    await watch_inbox()


if __name__ == "__main__":
    asyncio.run(main())
