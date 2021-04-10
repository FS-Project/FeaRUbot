# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# (c) Spechide - UniBorg
# Port From UniBorg to UserBot by @afdulfauzan

from telethon.tl import functions

from fearubot import CMD_HELP
from fearubot.events import register


@register(outgoing=True, pattern="^.create (b|g|c)(?: |$)(.*)")
async def telegraphs(grop):
    """ Untuk perintah .create, Membuat Grup & Channel baru """
    if not grop.text[0].isalpha() and grop.text[0] not in ("/", "#", "@", "!"):
        if grop.fwd_from:
            return
        type_of_group = grop.pattern_match.group(1)
        group_name = grop.pattern_match.group(2)
        if type_of_group == "b":
            try:
                result = await grop.client(
                    functions.messages.CreateChatRequest(  # pylint:disable=E0602
                        users=["@FerbotInd_bot"],
                        # Not enough users (to create a chat, for example)
                        # Telegram, no longer allows creating a chat with
                        # ourselves
                        title=group_name,
                    )
                )
                created_chat_id = result.chats[0].id
                result = await grop.client(
                    functions.messages.ExportChatInviteRequest(
                        peer=created_chat_id,
                    )
                )
                await grop.edit(
                    "Grup {} Anda Berhasil Dibuat. Klik [{}]({}) untuk gabung".format(
                        group_name, group_name, result.link
                    )
                )
            except Exception as e:  # pylint:disable=C0103,W0703
                await grop.edit(str(e))
        elif type_of_group == "g" or type_of_group == "c":
            try:
                r = await grop.client(
                    functions.channels.CreateChannelRequest(  # pylint:disable=E0602
                        title=group_name,
                        about="Selamat datang di Channel",
                        megagroup=False if type_of_group == "c" else True,
                    )
                )
                created_chat_id = r.chats[0].id
                result = await grop.client(
                    functions.messages.ExportChatInviteRequest(
                        peer=created_chat_id,
                    )
                )
                await grop.edit(
                    "{} Grup / Channel Anda Berhasil Dibuat. Klik [{}]({}) Untuk gabung".format(
                        group_name, group_name, result.link
                    )
                )
            except Exception as e:  # pylint:disable=C0103,W0703
                await grop.edit(str(e))


CMD_HELP.update(
    {
        "create": "\
Create\
\nPengunaan: Membuat channel / Group .\
\n\n.create g <nama grup>\
\nPengunaan: Membuat grup privat.\
\n\n.create b <nama grup>\
\nPengunaan: Membuat grup dengan menambahkan bot FerbotInd.\
\n\n.create c <nama channel>\
\nPengunaan: Membua channel.\
"
    }
)
