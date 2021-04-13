# INFO : ini merupakan copy source code dari repo one4ubot, dan sudah mendapatkan izin dari pemilik.
# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands related to the \
    Information Superhighway (yes, Internet). """

from datetime import datetime

from speedtest import Speedtest
from telethon import functions

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern="^.speed$")
async def speedtst(spd):
    """ For .speed command, use SpeedTest to check server speeds. """
    await spd.edit("`Speed tes berjalan . . .`")
    test = Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    await spd.edit(
        "`"
        "🕐 Dimulai pada "
        f"{result['timestamp']} \n\n"
        "⬇️ Download "
        f"{speed_convert(result['download'])} \n"
        "⬆️ Upload "
        f"{speed_convert(result['upload'])} \n"
        "📶 Ping "
        f"{result['ping']} \n"
        "✔️ ISP "
        f"{result['client']['isp']}"
        "`"
    )


def speed_convert(size):
    """
    Hi human, you can't read bytes?
    """
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@register(outgoing=True, pattern="^.dc$")
async def neardc(event):
    """ For .dc command, get the nearest datacenter information. """
    result = await event.client(functions.help.GetNearestDcRequest())
    await event.edit(
        f"Negara              : `{result.country}`\n"
        f"Pusat Data Terdekat : `{result.nearest_dc}`\n"
        f"Pusat Data ini      : `{result.this_dc}`"
    )


@register(outgoing=True, pattern="^.ping$")
async def pingme(pong):
    """ For .ping command, ping the userbot from any chat.  """
    start = datetime.now()
    await pong.edit("`📶 PONGG❗️`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await pong.edit("`📶 PONGG❗️\n%sms`" % (duration))


CMD_HELP.update(
    {
        "speed": ".speed\
    \nPenggunaan: Melakukan speedtest dan menunjukkan hasilnya."
    }
)
CMD_HELP.update(
    {
        "dc": ".dc\
    \nPenggunaan: Menemukan pusat data terdekat dari server Anda."
    }
)
CMD_HELP.update(
    {
        "ping": ".ping\
    \nPenggunaan: Menunjukkan berapa lama waktu yang dibutuhkan untuk melakukan ping ke bot Anda."
    }
)
