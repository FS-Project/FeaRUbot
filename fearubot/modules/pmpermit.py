# INFO : ini merupakan copy source code dari repo one4ubot, dan sudah mendapatkan izin dari pemilik.
# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for keeping control who PM you. """
import os

from sqlalchemy.exc import IntegrityError
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.tl.types import User

from fearubot import (
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    COUNT_PM,
    LASTMSG,
    LOGS,
    PM_AUTO_BAN,
)
from fearubot.events import register

DEFAULTUSER = os.environ.get("ALIVE_NAME")

# ========================= CONSTANTS ============================
DEF_UNAPPROVED_MSG = (
    f" Hello, Ada apa? {DEFAULTUSER} lagi offline!\n"
    " Jika sangat penting silahkan ketik yang anda inginkan "
    " dan **jangan spam jika tidak mau ter-block otomatis**\n\n"
    " - Protected By **FeaRUserbot**")
# =================================================================


@register(incoming=True, disable_edited=True, disable_errors=True)
async def permitpm(event):
    """ Prohibits people from PMing you without approval. \
        Will block retarded nibbas automatically. """
    if not PM_AUTO_BAN:
        return
    self_user = await event.client.get_me()
    if (
        event.is_private
        and event.chat_id != 777000
        and event.chat_id != self_user.id
        and not (await event.get_sender()).bot
    ):
        try:
            from userbot.modules.sql_helper.globals import gvarstatus
            from userbot.modules.sql_helper.pm_permit_sql import is_approved
        except AttributeError:
            return
        apprv = is_approved(event.chat_id)
        notifsoff = gvarstatus("NOTIF_OFF")

        # Use user custom unapproved message
        getmsg = gvarstatus("unapproved_msg")
        if getmsg is not None:
            UNAPPROVED_MSG = getmsg
        else:
            UNAPPROVED_MSG = DEF_UNAPPROVED_MSG

        # This part basically is a sanity check
        # If the message that sent before is Unapproved Message
        # then stop sending it again to prevent FloodHit
        if not apprv and event.text != UNAPPROVED_MSG:
            if event.chat_id in LASTMSG:
                prevmsg = LASTMSG[event.chat_id]
                # If the message doesn't same as previous one
                # Send the Unapproved Message again
                if event.text != prevmsg:
                    async for message in event.client.iter_messages(
                        event.chat_id, from_user="me", search=UNAPPROVED_MSG
                    ):
                        await message.delete()
                    await event.reply(f"`{UNAPPROVED_MSG}`")
            else:
                await event.reply(f"`{UNAPPROVED_MSG}`")
            LASTMSG.update({event.chat_id: event.text})
            if notifsoff:
                await event.client.send_read_acknowledge(event.chat_id)
            if event.chat_id not in COUNT_PM:
                COUNT_PM.update({event.chat_id: 1})
            else:
                COUNT_PM[event.chat_id] = COUNT_PM[event.chat_id] + 1

            if COUNT_PM[event.chat_id] > 4:
                await event.respond(
                        " **HEII, JANGAN SPAM, ANDA AKAN SAYA BLOCKIR!!**\n\n"
                        "- Protected By **FeaRUserbot**")

                try:
                    del COUNT_PM[event.chat_id]
                    del LASTMSG[event.chat_id]
                except KeyError:
                    if BOTLOG:
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            "Restart bot sekarang, jika tidak pesan pmpermit tidak berfungsi!",
                        )
                    LOGS.info("Pesan pmpermit tidak berfungsi sekarang!")
                    return

                await event.client(BlockRequest(event.chat_id))
                await event.client(ReportSpamRequest(peer=event.chat_id))

                if BOTLOG:
                    name = await event.client.get_entity(event.chat_id)
                    name0 = str(name.first_name)
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "["
                        + name0
                        + "](tg://user?id="
                        + str(event.chat_id)
                        + ")"
                        + " hanyalah sampah yang hanya ingin merusuhkan orang lain!",
                    )


@register(disable_edited=True, outgoing=True, disable_errors=True)
async def auto_accept(event):
    """ Will approve automatically if you texted them first. """
    if not PM_AUTO_BAN:
        return
    self_user = await event.client.get_me()
    if (
        event.is_private
        and event.chat_id != 777000
        and event.chat_id != self_user.id
        and not (await event.get_sender()).bot
    ):
        try:
            from userbot.modules.sql_helper.globals import gvarstatus
            from userbot.modules.sql_helper.pm_permit_sql import approve, is_approved
        except AttributeError:
            return

        # Use user custom unapproved message
        get_message = gvarstatus("unapproved_msg")
        if get_message is not None:
            UNAPPROVED_MSG = get_message
        else:
            UNAPPROVED_MSG = DEF_UNAPPROVED_MSG

        chat = await event.get_chat()
        if isinstance(chat, User):
            if is_approved(event.chat_id) or chat.bot:
                return
            async for message in event.client.iter_messages(
                event.chat_id, reverse=True, limit=1
            ):
                if (
                    message.text is not UNAPPROVED_MSG
                    and message.from_id == self_user.id
                ):
                    try:
                        approve(event.chat_id)
                    except IntegrityError:
                        return

                if is_approved(event.chat_id) and BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#AUTO-APPROVED\n"
                        + "Pengguna: "
                        + f"[{chat.first_name}](tg://user?id={chat.id})",
                    )


@register(outgoing=True, pattern=r"^.notifoff$")
async def notifoff(noff_event):
    """ For .notifoff command, stop getting notifications from unapproved PMs. """
    try:
        from userbot.modules.sql_helper.globals import addgvar
    except AttributeError:
        await noff_event.edit("*Berjalan pada mode Non-SQL!*")
        return
    addgvar("NOTIF_OFF", True)
    await noff_event.edit("*Notif dari PM yang tidak disetujui dibisukan!*")


@register(outgoing=True, pattern=r"^.notifon$")
async def notifon(non_event):
    """ For .notifoff command, get notifications from unapproved PMs. """
    try:
        from userbot.modules.sql_helper.globals import delgvar
    except AttributeError:
        await non_event.edit("*Berjalan pada mode Non-SQL!*")
        return
    delgvar("NOTIF_OFF")
    await non_event.edit("*Notifi dari PM yang tidak disetujui dihidupkan!*")


@register(outgoing=True, pattern=r"^.approve$")
async def approvepm(apprvpm):
    """ For .approve command, give someone the permissions to PM you. """
    try:
        from userbot.modules.sql_helper.globals import gvarstatus
        from userbot.modules.sql_helper.pm_permit_sql import approve
    except AttributeError:
        await apprvpm.edit("*Berjalan pada mode Non-SQL!*")
        return

    if apprvpm.reply_to_msg_id:
        reply = await apprvpm.get_reply_message()
        replied_user = await apprvpm.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        uid = replied_user.id

    else:
        aname = await apprvpm.client.get_entity(apprvpm.chat_id)
        name0 = str(aname.first_name)
        uid = apprvpm.chat_id

    # Get user custom msg
    getmsg = gvarstatus("unapproved_msg")
    if getmsg is not None:
        UNAPPROVED_MSG = getmsg
    else:
        UNAPPROVED_MSG = DEF_UNAPPROVED_MSG

    async for message in apprvpm.client.iter_messages(
        apprvpm.chat_id, from_user="me", search=UNAPPROVED_MSG
    ):
        await message.delete()

    try:
        approve(uid)
    except IntegrityError:
        await apprvpm.edit("*Pengguna telah di izinkan PM.*")
        return

    await apprvpm.edit(f"[{name0}](tg://user?id={uid}) *diizinkan PM!*")

    if BOTLOG:
        await apprvpm.client.send_message(
            BOTLOG_CHATID,
            "#APPROVED\n" + "Pengguna: " + f"[{name0}](tg://user?id={uid})",
        )


@register(outgoing=True, pattern=r"^.disapprove$")
async def disapprovepm(disapprvpm):
    try:
        from userbot.modules.sql_helper.pm_permit_sql import dissprove
    except BaseException:
        await disapprvpm.edit("*Berjalan pada mode Non-SQL!*")
        return

    if disapprvpm.reply_to_msg_id:
        reply = await disapprvpm.get_reply_message()
        replied_user = await disapprvpm.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        dissprove(aname)
    else:
        dissprove(disapprvpm.chat_id)
        aname = await disapprvpm.client.get_entity(disapprvpm.chat_id)
        name0 = str(aname.first_name)

    await disapprvpm.edit(
        f"[{name0}](tg://user?id={disapprvpm.chat_id}) `Membatalkan izin PM!`"
    )

    if BOTLOG:
        await disapprvpm.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={disapprvpm.chat_id})"
            " *Telah dilarang PM.*",
        )


@register(outgoing=True, pattern=r"^.block$")
async def blockpm(block):
    """ For .block command, block people from PMing you! """
    if block.reply_to_msg_id:
        reply = await block.get_reply_message()
        replied_user = await block.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        await block.client(BlockRequest(aname))
        await block.edit("*Anda saya block selamat tinggal!*")
        uid = replied_user.id
    else:
        await block.client(BlockRequest(block.chat_id))
        aname = await block.client.get_entity(block.chat_id)
        await block.edit("*Anda saya block selamat tinggal!*")
        name0 = str(aname.first_name)
        uid = block.chat_id

    try:
        from userbot.modules.sql_helper.pm_permit_sql import dissprove

        dissprove(uid)
    except AttributeError:
        pass

    if BOTLOG:
        await block.client.send_message(
            BOTLOG_CHATID,
            "#BLOCKED\n" + "Pengguna: " + f"[{name0}](tg://user?id={uid})",
        )


@register(outgoing=True, pattern=r"^.unblock$")
async def unblockpm(unblock):
    """ For .unblock command, let people PMing you again! """
    if unblock.reply_to_msg_id:
        reply = await unblock.get_reply_message()
        replied_user = await unblock.client.get_entity(reply.from_id)
        name0 = str(replied_user.first_name)
        await unblock.client(UnblockRequest(replied_user.id))
        await unblock.edit("*Anda telah di unblock!.*")

    if BOTLOG:
        await unblock.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={replied_user.id})" " *sudah di unblock!*",
        )


@register(outgoing=True, pattern=r"^.(set|get|reset) pm_msg(?: |$)(\w*)")
async def add_pmsg(cust_msg):
    """ Set your own Unapproved message. """
    if not PM_AUTO_BAN:
        return await cust_msg.edit("*Isi PM_AUTO_BAN pada variable menjadi = True*")
    try:
        import userbot.modules.sql_helper.globals as sql
    except AttributeError:
        await cust_msg.edit("*Berjalan pada mode Non-SQL!*")
        return

    await cust_msg.edit("*Prosesss...*")
    conf = cust_msg.pattern_match.group(1)

    custom_message = sql.gvarstatus("unapproved_msg")

    if conf.lower() == "set":
        message = await cust_msg.get_reply_message()
        status = "Saved"

        # check and clear user unapproved message first
        if custom_message is not None:
            sql.delgvar("unapproved_msg")
            status = "Updated"

        if message:
            # TODO: allow user to have a custom text formatting
            # eg: bold, underline, striketrough, link
            # for now all text are in monoscape
            msg = message.message  # get the plain text
            sql.addgvar("unapproved_msg", msg)
        else:
            return await cust_msg.edit("*Balas ke pesan!*")

        await cust_msg.edit("*Pesan disimpan sebagai pesan yang tidak disetujui*")

        if BOTLOG:
            await cust_msg.client.send_message(
                BOTLOG_CHATID, f"***{status} Pesan tidak diizinkan :*** \n\n{msg}"
            )

    if conf.lower() == "reset":
        if custom_message is not None:
            sql.delgvar("unapproved_msg")
            await cust_msg.edit("*Pesan yang tidak disetujui disetel ulang ke default*")
        else:
            await cust_msg.edit("*Anda belum menyetel pesan khusus*")

    if conf.lower() == "get":
        if custom_message is not None:
            await cust_msg.edit(
                "***Ini adalah pesan Anda jika ada yg PM tidak di setujui:***" f"\n\n{custom_message}"
            )
        else:
            await cust_msg.edit(
                "*Anda belum menyetel pesan untuk orang yang belum di approve\n"
                f"Menggunakan pesan default*: \n\n`{DEF_UNAPPROVED_MSG}`"
            )


CMD_HELP.update(
    {
        "pmpermit": "\
.approve\
\n*Penggunaan: Menyetujui orang melakukan PM.*\
\n\n.disapprove\
\n*Penggunaan: Menolak orang melakukan PM.*\
\n\n.block\
\n*Penggunaan: Block seseorang.*\
\n\n.unblock\
\n*Penggunann: Meng-unblock seseorang agar bisa PM anda.*\
\n\n.notifoff\
\n*Penggunann: Menghapus/Menonaktifkan pemberitahuan apa pun dari PM yang tidak disetujui.*\
\n\n.notifon\
\n*Penggunann: Izinkan pemberitahuan untuk PM yang tidak disetujui.*\
\n\n.set pm_msg <reply to msg>\
\n*Penggunann: Mengatur pesan khusus, akan terlihat bila seseorang PM anda sebelum di Approve*\
\n\n.get pm_msg\
\n*Penggunann: Melihat pesan khusus anda ketika di PM*\
\n\n.reset pm_msg\
\n*Penggunann: Menghapus pesan kostum anda ketika di PM*\
\n\n*Pesan khusus yang tidak disetujui saat ini tidak dapat menyetel teks berformat*\
\nseperti cetak tebal, garis bawah, tautan, dll. .\
\nPesan hanya akan dikirim dalam monoscape*"
    }
)
