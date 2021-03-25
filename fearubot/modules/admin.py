# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
"""
Userbot module to help you manage a group
"""

from asyncio import sleep
from os import remove

from telethon.errors import (
    BadRequestError,
    ChatAdminRequiredError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
    UserAdminInvalidError,
)
from telethon.errors.rpcerrorlist import (
    BadRequestError,
    MessageTooLongError,
    UserAdminInvalidError,
    UserIdInvalidError,
)
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    ChatAdminRights,
    ChatBannedRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
)

from fearubot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot
from fearubot.events import register

# =================== CONSTANT ===================
PP_TOO_SMOL = "Gambar terlalu kecil"
PP_ERROR = "Kegagalan saat memproses gambar"
NO_ADMIN = "Saya bukan admin!"
NO_PERM = "Saya tidak memiliki izin yang memadai!"
NO_SQL = "Berjalan pada mode Non-SQL!"

CHAT_PP_CHANGED = "Gambar Obrolan Diganti"
CHAT_PP_ERROR = (
    "Terdapat masalah saat memperbarui foto,"
    "mungkin karena saya bukan admin,"
    "atau tidak memiliki cukup hak."
)
INVALID_MEDIA = "Ekstensi Tidak Valid"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
# ================================================


@register(outgoing=True, pattern="^.setgpic$")
async def set_group_photo(gpic):
    """ Untuk merubah profile grup gunakan .setgpic """
    await gpic.edit("Sedang proses...")
    await sleep(1)
    if not gpic.is_group:
        await gpic.edit("Sepertinya ini bukan grup.")
        return
    replymsg = await gpic.get_reply_message()
    chat = await gpic.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    photo = None

    if not admin and not creator:
        await gpic.edit(NO_ADMIN)
        return

    if replymsg and replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await gpic.client.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split("/"):
            photo = await gpic.client.download_file(replymsg.media.document)
        else:
            await gpic.edit(INVALID_MEDIA)

    if photo:
        try:
            await gpic.client(
                EditPhotoRequest(gpic.chat_id, await gpic.client.upload_file(photo))
            )
            await gpic.edit(CHAT_PP_CHANGED)

        except PhotoCropSizeSmallError:
            await gpic.edit(PP_TOO_SMOL)
        except ImageProcessFailedError:
            await gpic.edit(PP_ERROR)


@register(outgoing=True, pattern="^.promote(?: |$)(.*)")
async def promote(promt):
    """ Untuk menjadikan seseorang ADMIN. Gunakan perintah .promote """
    # Get targeted chat
    chat = await promt.get_chat()
    # Grab admin status or creator in a chat
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, also return
    if not admin and not creator:
        await promt.edit(NO_ADMIN)
        return

    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )

    await promt.edit("Promoting....")
    user, rank = await get_user_from_event(promt)
    if not rank:
        rank = "Admeme(k)"  # Just in case.
    if user:
        pass
    else:
        return

    # Try to promote if current user is admin or creator
    try:
        await promt.client(EditAdminRequest(promt.chat_id, user.id, new_rights, rank))
        await promt.edit("Sukses Menjadikan Admin!")

    # If Telethon spit BadRequestError, assume
    # we don't have Promote permission
    except BadRequestError:
        await promt.edit(NO_PERM)
        return

    # Announce to the logging group if we have promoted successfully
    if BOTLOG:
        await promt.client.send_message(
            BOTLOG_CHATID,
            "#PROMOTE\n"
            f"PENGGUNA: [{user.first_name}](tg://user?id={user.id})\n"
            f"Grup: {promt.chat.title}(`{promt.chat_id}`)",
        )


@register(outgoing=True, pattern="^.demote(?: |$)(.*)")
async def demote(dmod):
    """ Untuk Menurunkan Seseorang Admin Gunakan .demote """
    # Admin right check
    chat = await dmod.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await dmod.edit(NO_ADMIN)
        return

    # If passing, declare that we're going to demote
    await dmod.edit("Demoting...")
    rank = "Admeme(k)"  # dummy rank, lol.
    user = await get_user_from_event(dmod)
    user = user[0]
    if user:
        pass
    else:
        return

    # New rights after demotion
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    # Edit Admin Permission
    try:
        await dmod.client(EditAdminRequest(dmod.chat_id, user.id, newrights, rank))

    # If we catch BadRequestError from Telethon
    # Assume we don't have permission to demote
    except BadRequestError:
        await dmod.edit(NO_PERM)
        return
    await dmod.edit("Sukses Menurunkan Admin!")

    # Announce to the logging group if we have demoted successfully
    if BOTLOG:
        await dmod.client.send_message(
            BOTLOG_CHATID,
            "#DEMOTE\n"
            f"PENGGUNA: [{user.first_name}](tg://user?id={user.id})\n"
            f"Grup: {dmod.chat.title}(`{dmod.chat_id}`)",
        )


@register(outgoing=True, pattern="^.ban(?: |$)(.*)")
async def ban(bon):
    """ Untuk Ban seseorang Gunakan .ban """
    # Here laying the sanity check
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await bon.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(bon)
    if user:
        pass
    else:
        return

    # Announce that we're going to whack the pest
    await bon.edit("Proses Ban...!")

    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        await bon.edit(NO_PERM)
        return
    # Helps ban group join spammers more easily
    try:
        reply = await bon.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        await bon.edit("Saya tidak memiliki hak Ban! Tapi tetap saja dia dilarang!")
        return
    # Delete message and then tell that the command
    # is done gracefully
    # Shout out the ID, so that fedadmins can fban later
    if reason:
        await bon.edit(
            f"{user.first_name} Telah DIBan. !!\
        \nID: {str(user.id)}\
        \nAlasan: {reason}"
        )
    else:
        await bon.edit(
            f"{user.first_name} Telah DIban. !!\
        \nID: {str(user.id)}"
        )
    # Announce to the logging group if we have banned the person
    # successfully!
    if BOTLOG:
        await bon.client.send_message(
            BOTLOG_CHATID,
            "#BAN\n"
            f"Pengguna: [{user.first_name}](tg://user?id={user.id})\n"
            f"Grup: {bon.chat.title}({bon.chat_id})",
        )


@register(outgoing=True, pattern="^.unban(?: |$)(.*)")
async def nothanos(unbon):
    """ Untuk Unban Gunakan .unban """
    # Here laying the sanity check
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await unbon.edit(NO_ADMIN)
        return

    # If everything goes well...
    await unbon.edit("Proses Unban...")

    user = await get_user_from_event(unbon)
    user = user[0]
    if user:
        pass
    else:
        return

    try:
        await unbon.client(EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await unbon.edit("```Sukses Unban.```")

        if BOTLOG:
            await unbon.client.send_message(
                BOTLOG_CHATID,
                "#UNBAN\n"
                f"Pengguna: [{user.first_name}](tg://user?id={user.id})\n"
                f"Grup: {unbon.chat.title}(`{unbon.chat_id}`)",
            )
    except UserIdInvalidError:
        await unbon.edit("Hmmmm, tenaga unban saya rusak!")


@register(outgoing=True, pattern="^.mute(?: |$)(.*)")
async def spider(spdr):
    """
    This function is basically muting peeps
    """
    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.spam_mute_sql import mute
    except AttributeError:
        await spdr.edit(NO_SQL)
        return

    # Admin or creator check
    chat = await spdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await spdr.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(spdr)
    if user:
        pass
    else:
        return

    self_user = await spdr.client.get_me()

    if user.id == self_user.id:
        await spdr.edit("Terlalu berisik, Diam sekarang...\n(ヘ･_･)ヘ┳━┳")
        return

    # If everything goes well, do announcing and mute
    await spdr.edit("Gets a tape!")
    if mute(spdr.chat_id, user.id) is False:
        return await spdr.edit("Error! Pengguna telah dimute sebelumnya.")
    else:
        try:
            await spdr.client(EditBannedRequest(spdr.chat_id, user.id, MUTE_RIGHTS))

            # Announce that the function is done
            if reason:
                await spdr.edit(f"Diam dengan aman !!\nAlasan: {reason}")
            else:
                await spdr.edit("Diam dengan aman !!")

            # Announce to logging group
            if BOTLOG:
                await spdr.client.send_message(
                    BOTLOG_CHATID,
                    "#MUTE\n"
                    f"Pengguna: [{user.first_name}](tg://user?id={user.id})\n"
                    f"Grup: {spdr.chat.title}(`{spdr.chat_id}`)",
                )
        except UserIdInvalidError:
            return await spdr.edit("Hmmmm. Tenaga mute saya rusak!")


@register(outgoing=True, pattern="^.unmute(?: |$)(.*)")
async def unmoot(unmot):
    """ Untuk Unmute Gunakan .unmute """
    # Admin or creator check
    chat = await unmot.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await unmot.edit(NO_ADMIN)
        return

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.spam_mute_sql import unmute
    except AttributeError:
        await unmot.edit(NO_SQL)
        return

    # If admin or creator, inform the user and start unmuting
    await unmot.edit("```Proses Unmute...```")
    user = await get_user_from_event(unmot)
    user = user[0]
    if user:
        pass
    else:
        return

    if unmute(unmot.chat_id, user.id) is False:
        return await unmot.edit("Error! User sudah di unmute sebelumnya.")
    else:

        try:
            await unmot.client(EditBannedRequest(unmot.chat_id, user.id, UNBAN_RIGHTS))
            await unmot.edit("```Sukses unmute```")

        except UserIdInvalidError:
            await unmot.edit("Hmmmm. Tenaga unmute saya rusak!")
            return

        if BOTLOG:
            await unmot.client.send_message(
                BOTLOG_CHATID,
                "#UNMUTE\n"
                f"Pengguna: [{user.first_name}](tg://user?id={user.id})\n"
                f"Grup: {unmot.chat.title}(`{unmot.chat_id}`)",
            )


@register(incoming=True, disable_errors=True)
async def muter(moot):
    """ Digunakan untuk menghapus pesan dari orang yang dimute """
    try:
        from userbot.modules.sql_helper.gmute_sql import is_gmuted
        from userbot.modules.sql_helper.spam_mute_sql import is_muted
    except AttributeError:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                try:
                    await moot.delete()
                    await moot.client(
                        EditBannedRequest(moot.chat_id, moot.sender_id, rights)
                    )
                except (
                    BadRequestError,
                    UserAdminInvalidError,
                    ChatAdminRequiredError,
                    UserIdInvalidError,
                ):
                    await moot.client.send_read_acknowledge(moot.chat_id, moot.id)
    for i in gmuted:
        if i.sender == str(moot.sender_id):
            await moot.delete()


@register(outgoing=True, pattern="^.ungmute(?: |$)(.*)")
async def ungmoot(un_gmute):
    """ Untuk ungmute seseorang yang di gmute userbot, Gunakan .ungmute """
    # Admin or creator check
    chat = await un_gmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await un_gmute.edit(NO_ADMIN)
        return

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import ungmute
    except AttributeError:
        await un_gmute.edit(NO_SQL)
        return

    user = await get_user_from_event(un_gmute)
    user = user[0]
    if user:
        pass
    else:
        return

    # If pass, inform and start ungmuting
    await un_gmute.edit("```Proses ungmute...```")

    if ungmute(user.id) is False:
        await un_gmute.edit("Error! User mungkin tidak di gmute.")
    else:
        # Inform about success
        await un_gmute.edit("```Sukses ungmute```")

        if BOTLOG:
            await un_gmute.client.send_message(
                BOTLOG_CHATID,
                "#UNGMUTE\n"
                f"Pengguna: [{user.first_name}](tg://user?id={user.id})\n"
                f"Grup: {un_gmute.chat.title}(`{un_gmute.chat_id}`)",
            )


@register(outgoing=True, pattern="^.gmute(?: |$)(.*)")
async def gspider(gspdr):
    """ Untuk Gmute sesorang, Gunakan .gmute """
    # Admin or creator check
    chat = await gspdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await gspdr.edit(NO_ADMIN)
        return

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import gmute
    except AttributeError:
        await gspdr.edit(NO_SQL)
        return

    user, reason = await get_user_from_event(gspdr)
    if user:
        pass
    else:
        return

    # If pass, inform and start gmuting
    await gspdr.edit("Mengambil lakban besar yang lengket dan ikat dia!!")
    if gmute(user.id) is False:
        await gspdr.edit("Error! User sudah ter gmute.\nMenggulung kembali lakbannya.")
    else:
        if reason:
            await gspdr.edit(f"Dimute secara global!\nAlasan: {reason}")
        else:
            await gspdr.edit("Dimute secara global!")

        if BOTLOG:
            await gspdr.client.send_message(
                BOTLOG_CHATID,
                "#GMUTE\n"
                f"Pengguna: [{user.first_name}](tg://user?id={user.id})\n"
                f"Grup: {gspdr.chat.title}(`{gspdr.chat_id}`)",
            )


@register(outgoing=True, pattern="^.zombies(?: |$)(.*)", groups_only=False)
async def rm_deletedacc(show):
    """ Untuk melihat akun hantu / terhapus / zombie Di dalam grup, Gunakan .zombies. """

    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "Tidak terdapat akun hantu / terhapus / zombie Di dalam grup, Grup sudah bersih"

    if con != "clean":
        await show.edit("Sedang mencari akun hantu / terhapus / zombie Di dalam grup..")
        async for user in show.client.iter_participants(show.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = f"Terdapat **{del_u}** akun hantu / terhapus / zombie Di dalam grup,\
            \nBersihkan dengan menggunakan .zombies clean"
        await show.edit(del_status)
        return

    # Here laying the sanity check
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await show.edit("Saya bukan admin disini!")
        return

    await show.edit("Penghapusan akun hantu / terhapus / zombie di grup...\nApakah saya bisa melakukanya?!?!")
    del_u = 0
    del_a = 0

    async for user in show.client.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                await show.edit("Saya tidak memiliki hak Ban dalam grup ini")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await show.client(EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"Dibersihkan **{del_u}** akun hantu / terhapus / zombie di grup"

    if del_a > 0:
        del_status = f"Dibersihkan **{del_u}** akun hantu / terhapus / zombie di grup \
        \n**{del_a}** akun admin yang telah terhapus, tidak akan dihapus"

    await show.edit(del_status)
    await sleep(2)
    await show.delete()

    if BOTLOG:
        await show.client.send_message(
            BOTLOG_CHATID,
            "#CLEANUP\n"
            f"Dibersihkan **{del_u}** akun hantu / terhapus / zombie di grup !!\
            \nGrup: {show.chat.title}({show.chat_id})",
        )


@register(outgoing=True, pattern="^.tagall$")
async def tagaso(event):
    """ Untuk memanggil seluruh anggota, Gunakan .all"""
    if event.fwd_from:
        return
    await event.delete()
    mentions = "@all"
    chat = await event.get_input_chat()
    async for user in bot.iter_participants(chat, 500):
        mentions += f"[\u2063](tg://user?id={user.id})"
    await bot.send_message(chat, mentions, reply_to=event.message.reply_to_msg_id)


@register(outgoing=True, pattern="^.listadmin(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    info = await event.client.get_entity(event.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "**Admin di Grup {}**: \n".format(title)
    should_mention_admins = False
    reply_message = None
    pattern_match_str = event.pattern_match.group(1)
    if "m" in pattern_match_str:
        should_mention_admins = True
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
    input_str = event.pattern_match.group(1)
    to_write_chat = await event.get_input_chat()
    chat = None
    if not input_str:
        chat = to_write_chat
    else:
        try:
            chat = await bot.get_entity(input_str)
        except Exception as e:
            await event.edit(str(e))
            return None
    try:
        async for x in bot.iter_participants(chat, filter=ChannelParticipantsAdmins):
            if not x.deleted:
                if isinstance(x.participant, ChannelParticipantCreator):
                    mentions += "\n 👑 [{}](tg://user?id={}) {}".format(
                        x.first_name, x.id, x.id
                    )
        mentions += "\n"
        async for x in bot.iter_participants(chat, filter=ChannelParticipantsAdmins):
            if not x.deleted:
                if isinstance(x.participant, ChannelParticipantAdmin):
                    mentions += "\n 🔰 [{}](tg://user?id={}) {}".format(
                        x.first_name, x.id, x.id
                    )

    #  mentions += "\n 💘 [Deleted Account](tg://user?id=689811472) `689811472`"

    except Exception as e:
        mentions += " " + str(e) + "\n"
    if should_mention_admins:
        if reply_message:
            await reply_message.reply(mentions)
        else:
            await event.reply(mentions)
        await event.delete()
    else:
        await event.edit(mentions)


@register(outgoing=True, pattern="^.pin(?: |$)(.*)")
async def pin(msg):
    """ Untuk pin pesan, Gunakan .pin dan balas pesannya. """
    # Admin or creator check
    chat = await msg.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await msg.edit(NO_ADMIN)
        return

    to_pin = msg.reply_to_msg_id

    if not to_pin:
        await msg.edit("Balas pesan yang ingin di pin.")
        return

    options = msg.pattern_match.group(1)

    is_silent = True

    if options.lower() == "loud":
        is_silent = False

    try:
        await msg.client(UpdatePinnedMessageRequest(msg.to_id, to_pin, is_silent))
    except BadRequestError:
        await msg.edit(NO_PERM)
        return

    await msg.edit("Sukses pin pesan!")

    user = await get_user_from_id(msg.from_id, msg)

    if BOTLOG:
        await msg.client.send_message(
            BOTLOG_CHATID,
            "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"Grup: {msg.chat.title}({msg.chat_id})\n"
            f"LOUD: {not is_silent}",
        )


@register(outgoing=True, pattern="^.kick(?: |$)(.*)")
async def kick(usr):
    """ Untuk mengeluarkan anggota, Gunakan .kick. """
    # Admin or creator check
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await usr.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(usr)
    if not user:
        await usr.edit("Gagal menendang pengguna!.")
        return

    await usr.edit("Proses mengeluarkan...")

    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(1)
    except Exception as e:
        await usr.edit(NO_PERM + f"\n{str(e)}")
        return

    if reason:
        await usr.edit(
            f"Dikeluarkan [{user.first_name}](tg://user?id={user.id})!\nAlasan: {reason}"
        )
    else:
        await usr.edit(f"Dikeluarkan [{user.first_name}](tg://user?id={user.id})`!`")

    if BOTLOG:
        await usr.client.send_message(
            BOTLOG_CHATID,
            "#KICK\n"
            f"Pengguna: [{user.first_name}](tg://user?id={user.id})\n"
            f"Grup: {usr.chat.title}(`{usr.chat_id}`)\n",
        )


@register(outgoing=True, pattern="^.listuser ?(.*)")
async def get_users(show):
    """ Untuk melihat anggota, Gunakan .users """
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "**Anggota di Grup {}**: \n".format(title)
    try:
        if not show.pattern_match.group(1):
            async for user in show.client.iter_participants(show.chat_id):
                if not user.deleted:
                    mentions += (
                        f"\n ⚜️ [{user.first_name}](tg://user?id={user.id}) {user.id}"
                    )
                else:
                    mentions += f"\nAkun terhapus {user.id}"
        else:
            searchq = show.pattern_match.group(1)
            async for user in show.client.iter_participants(
                show.chat_id, search=f"{searchq}"
            ):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) {user.id}"
                    )
                else:
                    mentions += f"\nAkun terhapus {user.id}"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit("Hmmmm, daftar anggota sangat banyak. Lihat daftar anggota di File.")
        file = open("ListAnggota.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "ListAnggota.txt",
            caption="Users in {}".format(title),
            reply_to=show.id,
        )
        remove("ListAnggota.txt")


async def get_user_from_event(event):
    """ Dapatkan pengguna dari argumen atau pesan balasan. """
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id and not len(args) == 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("Berikan nama pengguna, id, atau balas pesannya!")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return user_obj, extra


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj


@register(outgoing=True, pattern="^.usersdel ?(.*)")
async def get_usersdel(show):
    """ Untuk melihat seluruh anggota yang akun terhapus,Gunakan .usersdel . """
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "Anggota akun terhapus di {}: \n".format(title)
    try:
        if not show.pattern_match.group(1):
            async for user in show.client.iter_participants(show.chat_id):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) {user.id}"
                    )
        #       else:
        #                mentions += f"\nDeleted Account `{user.id}`"
        else:
            searchq = show.pattern_match.group(1)
            async for user in show.client.iter_participants(
                show.chat_id, search=f"{searchq}"
            ):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) {user.id}"
                    )
        #       else:
    #              mentions += f"\nDeleted Account `{user.id}`"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit(
            "Hmmmm, ini grup yang sangat ramai. Lihat file untuk melihat daftarnya."
        )
        file = open("userslist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "ListAnggotaAkunTerhapus.txt",
            caption="Users in {}".format(title),
            reply_to=show.id,
        )
        remove("ListAnggotaAkunTerhapus.txt")


async def get_userdel_from_event(event):
    """ Dapatkan pengguna yang dihapus dari argumen atau pesan balasan. """
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id and not len(args) == 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("Berikan nama pengguna, id, atau balas pesan dari akun terhapus!")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return user_obj, extra


async def get_userdel_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj


@register(outgoing=True, pattern="^.listbot(?: |$)(.*)")
async def _(event):
    """ Untuk melihat daftar bot disini, Gunakan .bots. """
    if event.fwd_from:
        return
    info = await event.client.get_entity(event.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "**Bot di Grup {}**: \n".format(title)
    input_str = event.pattern_match.group(1)
    to_write_chat = await event.get_input_chat()
    chat = None
    if not input_str:
        chat = to_write_chat
    else:
        try:
            chat = await bot.get_entity(input_str)
        except Exception as e:
            await event.edit(str(e))
            return None
    try:
        async for x in bot.iter_participants(chat, filter=ChannelParticipantsBots):
            if isinstance(x.participant, ChannelParticipantAdmin):
                mentions += "\n 👑 [{}](tg://user?id={}) {}".format(
                    x.first_name, x.id, x.id
                )
            else:
                mentions += "\n [{}](tg://user?id={}) {}".format(
                    x.first_name, x.id, x.id
                )
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await event.edit(mentions)


CMD_HELP.update(
    {
        "admin": ".promote <username/balas pesannya> <tittle (opsional)>\
\nPenggunaan: Menjadikan pengguna sebagai admin dalam grup.\
\n\n.demote <username/balas pesannya>\
\nPenggunaan: Mencabut izin admin orang tersebut dalam grup.\
\n\n.ban <username/balas pesannya> <alasan (opsional)>\
\nPenggunaan: Ban seseorang dari grup.\
\n\n.unban <username/balas pesannya>\
\nPenggunaan: Menghapus Ban dari orang dalam grup.\
\n\n.mute <username/balas pesannya> <alasan (opsional)>\
\nPenggunaan: Memute orang dalam grub, juga berfungsi pada admin.\
\n\n.unmute <username/balas pesannya>\
\nPenggunaan: Menghapus seseorang dalam daftar mute.\
\n\n.gmute <username/balas pesannya> <Alasan (opsional)>\
\nPenggunaan: Memute orang di semua grup yang memiliki kesamaan dengan Anda dan dia.\
\n\n.ungmute <username/balas pesannya>\
\nPenggunaan: Balas pesan seseorang dengan .ungmute untuk menghapusnya dari daftar yang digmute.\
\n\n.zombies\
\nPenggunaan: Mencari akun yang dihapus dalam grup, Gunakan .zombies clean untuk menghapus akun yang dihapus dari grup.\
\n\n.tagall\
\nPenggunaan: Tag semua anggota di grup.\
\n\n.listadmin\
\nPenggunaan: Mengambil daftar admin di grup.\
\n\n.listbot\
\nPenggunaan: Mengambil daftar bot di obrolan.\
\n\n.listuser or .users <nama anggota>\
\nPenggunaan: Menampilkan anggota di grup.\
\n\n.setgppic <balas gambarnya>\
\nPenggunaan: Mengganti atau memasang logo grup."
    }
)
