# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot start point """

from importlib import import_module
from sys import argv

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from fearubot import LOGS, bot
from fearubot.modules import ALL_MODULES


INVALID_PH = '\nERROR: Nomor Telepon yang dimasukkan TIDAK VALID' \
             '\n Tips: Gunakan Kode Negara, misal: +62.' \
             '\n atau cek nomor telepon yang dimasukan!'

try:
    bot.start()
except PhoneNumberInvalidError:
    print(INVALID_PH)
    exit(1)

for module_name in ALL_MODULES:
    imported_module = import_module("fearubot.modules." + module_name)

LOGS.info("Anda menjalankan FeaRUbot [v1.0]")

LOGS.info(
    "Selamat, userbot FeaRUbot Anda sekarang berjalan !! Uji dengan mengetik .alive / .on / .help di mana pun.")

if len(argv) not in (1, 3, 4):
    bot.disconnect()
else:
    bot.run_until_disconnected()
