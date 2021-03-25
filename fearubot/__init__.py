# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os
import re
import time
from sys import version_info
from logging import basicConfig, getLogger, INFO, DEBUG
from distutils.util import strtobool as sb
from math import ceil

from pylast import LastFMNetwork, md5
from pySmartDL import SmartDL
from pymongo import MongoClient
from redis import StrictRedis
from dotenv import load_dotenv
from requests import get
from telethon.sync import TelegramClient, custom, events
from telethon.sessions import StringSession

load_dotenv("config.env")

StartTime = time.time()

CMD_LIST = {}
# for later purposes
CMD_HELP = {}
INT_PLUG = ""
LOAD_PLUG = {}

# Bot Logs setup:
CONSOLE_LOGGER_VERBOSE = sb(os.environ.get(
    "CONSOLE_LOGGER_VERBOSE") or "False")

if CONSOLE_LOGGER_VERBOSE:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=DEBUG,
    )
else:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=INFO)
LOGS = getLogger(__name__)

if version_info[0] < 3 or version_info[1] < 8:
    LOGS.info(
        "Anda HARUS meakai versi python minimal 3.8"
        "Beberapa fitur bergantung pada ini. Bot dihentikan."
    )
    quit(1)

# Check if the config was edited by using the already used variable.
# Basically, its the 'virginity check' for the config file ;)
CONFIG_CHECK = (os.environ.get(
    "___________PLOX_______REMOVE_____THIS_____LINE__________") or None)

if CONFIG_CHECK:
    LOGS.info(
        "Harap hapus baris yang disebutkan pada hashtag pertama dari file config.env"
    )
    quit(1)

# Telegram App KEY and HASH
API_KEY = os.environ.get("API_KEY") or None
API_HASH = os.environ.get("API_HASH") or None

# Userbot Session String
STRING_SESSION = os.environ.get("STRING_SESSION") or None

# Deezloader
DEEZER_ARL_TOKEN = os.environ.get("DEEZER_ARL_TOKEN") or None

# Logging channel/group ID configuration.
BOTLOG_CHATID = int(os.environ.get("BOTLOG_CHATID") or "False")

# Userbot logging feature switch.
BOTLOG = sb(os.environ.get("BOTLOG") or "True")
if BOTLOG:
    LOGSPAMMER = sb(os.environ.get("LOGSPAMMER") or "False")
else:
    LOGSPAMMER = False

# Bleep Blop, this is a bot ;)
PM_AUTO_BAN = sb(os.environ.get("PM_AUTO_BAN") or "True")

# Heroku Credentials for updater.
HEROKU_MEMEZ = sb(os.environ.get("HEROKU_MEMEZ") or "True")
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME") or None
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY") or None

# Github Credentials for updater and Gitupload.
GIT_REPO_NAME = os.environ.get("GIT_REPO_NAME") or None
GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN") or None

# Custom (forked) repo URL and BRANCH for updater.
UPSTREAM_REPO_URL = (os.environ.get("UPSTREAM_REPO_URL")
                     or "https://github.com/FS-Project/FeaRUbot.git")
UPSTREAM_REPO_BRANCH = os.environ.get("UPSTREAM_REPO_BRANCH") or "main"

# Console verbose logging
CONSOLE_LOGGER_VERBOSE = sb(os.environ.get(
    "CONSOLE_LOGGER_VERBOSE") or "False")

# SQL Database URI
DB_URI = os.environ.get("DATABASE_URL") or None

# OCR API key
OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY") or None

# remove.bg API key
REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY") or None

# Chrome Driver and Headless Google Chrome Binaries
CHROME_DRIVER = os.environ.get("CHROME_DRIVER") or None
GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN") or None

# OpenWeatherMap API Key
OPEN_WEATHER_MAP_APPID = os.environ.get("OPEN_WEATHER_MAP_APPID") or None
WEATHER_DEFCITY = os.environ.get("WEATHER_DEFCITY") or None
WEATHER_DEFLANG = os.environ.get("WEATHER_DEFLANG") or None

# Genius lyrics API
GENIUS = os.environ.get("GENIUS_ACCESS_TOKEN") or None

# Wolfram Alpha API
WOLFRAM_ID = os.environ.get("WOLFRAM_ID") or None

# Anti Spambot Config
ANTI_SPAMBOT = sb(os.environ.get("ANTI_SPAMBOT") or "True")
ANTI_SPAMBOT_SHOUT = sb(os.environ.get("ANTI_SPAMBOT_SHOUT") or "True")

# Default .alive name
ALIVE_NAME = os.environ.get("ALIVE_NAME") or None

# Default .alive logo
ALIVE_LOGO = os.environ.get("ALIVE_LOGO") or "https://i.ibb.co/9Ns5jsZ/logo-fearubot.jpg"

# Time & Date - Country and Time Zone
COUNTRY = str(os.environ.get("COUNTRY") or "ID")
TZ_NUMBER = int(os.environ.get("TZ_NUMBER") or 1)

# Version of FeRuBoT
USERBOT_VERSION = os.environ.get("USERBOT_VERSION") or "1.0"

# User Terminal alias
USER_TERM_ALIAS = os.environ.get("USER_TERM_ALIAS") or "FeaRUbot"

# Updater alias
UPDATER_ALIAS = os.environ.get("UPDATER_ALIAS") or "FeRuBoT"

# Zipfile module
ZIP_DOWNLOAD_DIRECTORY = os.environ.get("ZIP_DOWNLOAD_DIRECTORY") or "./zips"

# Clean Welcome
CLEAN_WELCOME = sb(os.environ.get("CLEAN_WELCOME") or "True")

# Last.fm Module
BIO_PREFIX = os.environ.get("BIO_PREFIX") or None
DEFAULT_BIO = os.environ.get("DEFAULT_BIO") or None

LASTFM_API = os.environ.get("LASTFM_API") or None
LASTFM_SECRET = os.environ.get("LASTFM_SECRET") or None
LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME") or None
LASTFM_PASSWORD_PLAIN = os.environ.get("LASTFM_PASSWORD") or None
LASTFM_PASS = md5(LASTFM_PASSWORD_PLAIN)
if LASTFM_API is not None:
    lastfm = LastFMNetwork(
        api_key=LASTFM_API,
        api_secret=LASTFM_SECRET,
        username=LASTFM_USERNAME,
        password_hash=LASTFM_PASS,
    )
else:
    lastfm = None

# Google Drive Module
G_DRIVE_DATA = os.environ.get("G_DRIVE_DATA") or None
G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID") or None
G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET") or None
G_DRIVE_AUTH_TOKEN_DATA = os.environ.get("G_DRIVE_AUTH_TOKEN_DATA") or None
G_DRIVE_FOLDER_ID = os.environ.get("G_DRIVE_FOLDER_ID") or None
TEMP_DOWNLOAD_DIRECTORY = os.environ.get(
    "TMP_DOWNLOAD_DIRECTORY") or "./downloads"

# Uptobox
USR_TOKEN = os.environ.get("USR_TOKEN_UPTOBOX", None)


# Setting Up CloudMail.ru and MEGA.nz extractor binaries,
# and giving them correct perms to work properly.
if not os.path.exists("bin"):
    os.mkdir("bin")

binaries = {
    "https://raw.githubusercontent.com/adekmaulana/megadown/master/megadown": "bin/megadown",
    "https://raw.githubusercontent.com/yshalsager/cmrudl.py/master/cmrudl.py": "bin/cmrudl",
}

for binary, path in binaries.items():
    downloader = SmartDL(binary, path, progress_bar=False)
    downloader.start()
    os.chmod(path, 0o755)

# 'bot' variable
if STRING_SESSION:
    # pylint: disable=invalid-name
    bot = TelegramClient(StringSession(STRING_SESSION), API_KEY, API_HASH)
else:
    # pylint: disable=invalid-name
    bot = TelegramClient("userbot", API_KEY, API_HASH)


async def check_botlog_chatid():
    if not BOTLOG:
        return

    entity = await bot.get_entity(BOTLOG_CHATID)
    if entity.default_banned_rights.send_messages:
        LOGS.info(
            "BOTLOG_CHATID tidak valid!"
            "Periksa environment variabel/file config.env Anda.")
        quit(1)


with bot:
    try:
        bot.loop.run_until_complete(check_botlog_chatid())
    except BaseException:
        LOGS.info(
            "BOTLOG_CHATID tidak valid!"
            "Periksa environment variabel/file config.env Anda."
        )
        quit(1)

# Global Variables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
ENABLE_KILLME = True
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
ZALG_LIST = {}

def paginate_help(page_number, loaded_modules, prefix):
    number_of_rows = 5
    number_of_cols = 4
    helpable_modules = [p for p in loaded_modules if not p.startswith("_")]
    helpable_modules = sorted(helpable_modules)
    modules = [
        custom.Button.inline("{} {}".format("⚙️", x), data="ub_modul_{}".format(x))
        for x in helpable_modules
    ]
    pairs = list(zip(modules[::number_of_cols],
                     modules[1::number_of_cols],
                     modules[2::number_of_cols]))
    if len(modules) % number_of_cols == 1:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / number_of_rows)
    modulo_page = page_number % max_num_pages
    if len(pairs) > number_of_rows:
        pairs = pairs[
            modulo_page * number_of_rows: number_of_rows * (modulo_page + 1)
        ] + [
            (
                custom.Button.inline(
                    "⇇", data="{}_prev({})".format(prefix, modulo_page)
                ),
                custom.Button.inline(
                    "⇉", data="{}_next({})".format(prefix, modulo_page)
                )
            )
        ]
    return pairs


with bot:
    try:
        tgbot = TelegramClient(
            "TG_BOT_TOKEN",
            api_id=API_KEY,
            api_hash=API_HASH).start(
            bot_token=BOT_TOKEN)

        dugmeler = CMD_HELP
        me = bot.get_me()
        uid = me.id

        @tgbot.on(events.NewMessage(pattern="/start"))
        async def handler(event):
            if event.message.from_id != uid:
                await event.reply("Saya [FeaRUbot](https://github.com/FS-Project/FeaRUbot) modul helper...\nGunakan bot mu, jangan gunakan akal mu")
            else:
                await event.reply(f"`Haloo, {ALIVE_NAME}\n\nSaya bekerja untuk anda :)`")

        @tgbot.on(events.InlineQuery)  # pylint:disable=E0602
        async def inline_handler(event):
            builder = event.builder
            result = None
            query = event.text
            if event.query.user_id == uid and query.startswith("@UserButt"):
                buttons = paginate_help(0, dugmeler, "helpme")
                result = builder.article(
                    "Harap Gunakan Hanya Dengan Perintah .help",
                    text="{}\nJumlah modul dimuat: {}\n               \n📌 **Main Menu** 📌\n".format(
                        "FeaRUbot modul helper",
                        len(dugmeler),
                    ),
                    buttons=buttons,
                    link_preview=False,
                )
            elif query.startswith("tb_btn"):
                result = builder.article(
                    "FeaRUbot Helper",
                    text="Lst module",
                    buttons=[],
                    link_preview=True)
            else:
                result = builder.article(
                    "FeaRUbot",
                    text="""Anda dapat mengubah akun Anda menjadi bot dan menggunakannya. Ingat, Anda tidak dapat mengelola bot orang lain! Semua detail instalasi dijelaskan dari alamat GitHub di bawah ini.""",
                    buttons=[
                        [
                            custom.Button.url(
                                "GitHub Repo",
                                "https://github.com/FS-Project/FeaRUbot"),
                            custom.Button.url(
                                "Support",
                                "https://t.me/Fernans1")],
                    ],
                    link_preview=False,
                )
            await event.answer([result] if result else None)

        @tgbot.on(
            events.callbackquery.CallbackQuery(  # pylint:disable=E0602
                data=re.compile(rb"helpme_next\((.+?)\)")
            )
        )
        async def on_plug_in_callback_query_handler(event):
            if event.query.user_id == uid:  # pylint:disable=E0602
                current_page_number = int(
                    event.data_match.group(1).decode("UTF-8"))
                buttons = paginate_help(
                    current_page_number + 1, dugmeler, "helpme")
                # https://t.me/TelethonChat/115200
                await event.edit(buttons=buttons)
            else:
                reply_pop_up_alert = "Silakan buat sendiri, jangan gunakan bot!"
                await event.answer(reply_pop_up_alert, cache_time=0, alert=True)

        @tgbot.on(
            events.callbackquery.CallbackQuery(  # pylint:disable=E0602
                data=re.compile(rb"helpme_prev\((.+?)\)")
            )
        )
        async def on_plug_in_callback_query_handler(event):
            if event.query.user_id == uid:  # pylint:disable=E0602
                current_page_number = int(
                    event.data_match.group(1).decode("UTF-8"))
                buttons = paginate_help(
                    current_page_number - 1, dugmeler, "helpme"  # pylint:disable=E0602
                )
                # https://t.me/TelethonChat/115200
                await event.edit(buttons=buttons)
            else:
                reply_pop_up_alert = "Silakan buat sendiri, jangan gunakan bot!"
                await event.answer(reply_pop_up_alert, cache_time=0, alert=True)

        @tgbot.on(
            events.callbackquery.CallbackQuery(  # pylint:disable=E0602
                data=re.compile(b"ub_modul_(.*)")
            )
        )
        async def on_plug_in_callback_query_handler(event):
            if event.query.user_id == uid:  # pylint:disable=E0602
                modul_name = event.data_match.group(1).decode("UTF-8")

                cmdhel = str(CMD_HELP[modul_name])
                if len(cmdhel) > 150:
                    help_string = (
                        str(CMD_HELP[modul_name]).replace('`', '')[:150] + "..."
                        + "\n\nBaca lainya, gunakan .help"
                        + modul_name
                        + " "
                    )
                else:
                    help_string = str(CMD_HELP[modul_name]).replace('`', '')

                reply_pop_up_alert = (
                    help_string
                    if help_string is not None
                    else "{} Tidak ada dokumen yang telah ditulis untuk modul itu.".format(
                        modul_name
                    )
                )
            else:
                reply_pop_up_alert = "Silakan buat sendiri, jangan gunakan bot!"

            await event.answer(reply_pop_up_alert, cache_time=0, alert=True)

    except BaseException:
        LOGS.info(
            "Dukungan untuk inline dinonaktifkan di bot Anda."
            "Untuk mengaktifkannya, tentukan token bot dan aktifkan mode inline pada bot Anda."
            "Jika menurut Anda ada masalah selain ini, hubungi kami.")
    try:
        bot.loop.run_until_complete(check_botlog_chatid())
    except BaseException:
        LOGS.info(
            "BOTLOG_CHATID tidak valid!"
            "Periksa environment variabel/file config.env Anda."
        )
        quit(1)
