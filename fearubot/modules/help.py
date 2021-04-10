# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot help command """

from fearubot import CMD_HELP
from fearubot.events import register


@register(outgoing=True, pattern="^.help(?: |$)(.*)")
async def help(event):
    """ Untuk perintah .help,"""
    args = event.pattern_match.group(1).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
        else:
            await event.edit("Harap tentukan nama modul yang valid.")
    else:
        string = ""
        for i in CMD_HELP:
            string += "`" + str(i)
            string += "`\t\t\t•\t\t\t "
        await event.edit(
            f"{string}"
            "\n\nPilihlah module yang anda inginkan.\
                        \n**Gunakan:** .help <nama module>"
        )
