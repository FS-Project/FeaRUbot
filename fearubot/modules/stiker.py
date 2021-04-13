# INFO : ini merupakan copy source code dari repo one4ubot, dan sudah mendapatkan izin dari pemilik.
# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for kanging stickers or making new ones. Thanks @rupansh"""

import io
import math
import random
import urllib.request
from os import remove

from PIL import Image
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    InputStickerSetID,
    MessageMediaPhoto,
)

from fearubot import CMD_HELP, bot
from fearubot.events import register

KANGING_STR = [
    "Gua curi yee, iri bilang boss...",
    "hmmm, mencuri itu tidak baik!",
    "Curi dolo yekan...",
    "Gua curi stiker ini, dan masukin ke packstiker (☉｡☉)...",
    "Pencurian stiker ini...",
    "Heiii, bagos niee!\nBoleh kah gua curi?!..",
    "Hmmm,gua mao curi stiker lo\nhehe.",
    "Gua curi yee, iri bilang sahabat.",
    "Gua curi yee, iri bilang euyy!",
    "Kelihatannya bagos (☉｡☉)!→\nGua akan curi ini...",
    "Stiker yang indah, akan gua curi ke packstiker gua",
    "Mantep juga nie, curi ahhh...",
    "Keren euy, Boleh kah gua curi?... ",
    "HEHEHE, gua curi ni stiker!",
    "Gua curi yee, iri bilang om!",
    "Wuihh, bagus juga nie, curi ahhh",
]


@register(outgoing=True, pattern="^.(?:curi|kang)\s?(.)?")
async def kang(args):
    """ For .kang command, kangs stickers or creates new ones. """
    user = await bot.get_me()
    if not user.username:
        user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    emojibypass = False
    is_anim = False
    emoji = None

    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            photo = await bot.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split("/"):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            await bot.download_file(message.media.document, photo)
            if (
                DocumentAttributeFilename(file_name="sticker.webp")
                in message.media.document.attributes
            ):
                emoji = message.media.document.attributes[1].alt
                if emoji != "":
                    emojibypass = True
        elif "tgsticker" in message.media.document.mime_type:
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            await bot.download_file(message.media.document, "AnimatedSticker.tgs")

            attributes = message.media.document.attributes
            for attribute in attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    emoji = attribute.alt

            emojibypass = True
            is_anim = True
            photo = 1
        else:
            await args.edit("`File tidak support!`")
            return
    else:
        await args.edit("`Saya gagal mencuri ini...`")
        return

    if photo:
        splat = args.text.split()
        if not emojibypass:
            emoji = "❤"
        pack = 1
        if len(splat) == 3:
            pack = splat[2]  # User sent both
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                # User wants to push into different pack, but is okay with
                # thonk as emote.
                pack = int(splat[1])
            else:
                # User sent just custom emote, wants to push to default
                # pack
                emoji = splat[1]

        packname = f"by_fearubot_{user.id}_{pack}"
        packnick = f"@{user.username} pack curian {pack}"
        cmd = "/newpack"
        file = io.BytesIO()

        if not is_anim:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"

        response = urllib.request.urlopen(
            urllib.request.Request(f"http://t.me/addstickers/{packname}")
        )
        htmlstr = response.read().decode("utf8").split("\n")

        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with bot.conversation("Stickers") as conv:
                await conv.send_message("/addsticker")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                while "120" in x.text:
                    pack += 1
                    packname = f"by_fearubot_{user.id}_{pack}"
                    packnick = f"@{user.username} pack curian {pack}"
                    await args.edit(
                        "Di tambah ke "
                        + str(pack)
                        + " karena ruang tidak mencukupi"
                    )
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "pack yang dipilih tidak valid.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file("AnimatedSticker.tgs")
                            remove("AnimatedSticker.tgs")
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        # Ensure user doesn't get spamming notifications
                        await conv.get_response()
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await args.edit(
                            f"`____TERCURY____ !\
                            \nPack baru dibuat!\
                            \nPack kamu bisa ditemukan [dimari](https://t.me/addstickers/{packname})",
                            parse_mode="md",
                        )
                        return
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Maaf, jenis file tidak valid." in rsp.text:
                    await args.edit(
                        "Gagal mencuri stiker, gunakan bot `@Stickers` untuk menambahkan stiker secara manual."
                    )
                    return
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/done")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
        else:
            await args.edit("Membuat Pack baru...")
            async with bot.conversation("Stickers") as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Maaf, jenis file tidak valid." in rsp.text:
                    await args.edit(
                        "Gagal mencuri stiker, gunakan bot `@Stickers` untuk menambahkan stiker secara manual."
                    )
                    return
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")
                # Ensure user doesn't get spamming notifications
                await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)

        await args.edit(
            f"`____TERCURY____`\
            \nPack dapat dilihat [dimari](https://t.me/addstickers/{packname})",
            parse_mode="md",
        )


async def resize_photo(photo):
    """ Resize the given photo to 512x512 """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image


@register(outgoing=True, pattern="^.stkrinfo$")
async def get_pack_info(event):
    if not event.is_reply:
        await event.edit("Saya tidak bisa mengambil info dari nol!")
        return

    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await event.edit("Balas stiker untuk mendapatkan detail pack")
        return

    try:
        stickerset_attr = rep_msg.document.attributes[1]
        await event.edit("Mengambil detail pack stiker, harap tunggu..")
    except BaseException:
        await event.edit("INI BUKAN STIKER!. Balas stikernya.")
        return

    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        await event.edit("INI BUKAN STIKER!. Balas stikernya.")
        return

    get_stickerset = await bot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            )
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)

    OUTPUT = (
        f"**Nama Stiker--------:** `{get_stickerset.set.title}\n`"
        f"**Nama Pendek Stiker-:** `{get_stickerset.set.short_name}`\n"
        f"**Official-----------:** `{get_stickerset.set.official}`\n"
        f"**Diarsipkan---------:** `{get_stickerset.set.archived}`\n"
        f"**Stiker di Pack-----:** `{len(get_stickerset.packs)}`\n"
        f"**Emoji di Pack------:**\n{' '.join(pack_emojis)}"
    )

    await event.edit(OUTPUT)


@register(outgoing=True, pattern="^.getsticker$")
async def sticker_to_png(sticker):
    if not sticker.is_reply:
        await sticker.edit("Informasi NULL untuk diambil...")
        return False

    img = await sticker.get_reply_message()
    if not img.document:
        await sticker.edit("Balas stikernya...")
        return False

    try:
        img.document.attributes[1]
    except Exception:
        await sticker.edit("**INI BUKAN STIKER!...**")
        return

    with io.BytesIO() as image:
        await sticker.client.download_media(img, image)
        image.name = "sticker.png"
        image.seek(0)
        try:
            await img.reply(file=image, force_document=True)
        except Exception:
            await sticker.edit("Error, gagal mengirim file...")
        else:
            await sticker.delete()
    return


CMD_HELP.update(
    {
        "stickers": ".kang atau .curi\
\nPenggunaan: Balas .kang atau .curi ke stiker atau gambar untuk mencuri dan ditambah di pack Anda.\
\n\n.kang [emoji]\
\nPenggunaan: Bekerja seperti .kang tetapi menggunakan emoji pilihan Anda.\
\n\n.kang [nomor]\
\nPenggunaan: Curi stiker/gambar dan dimasukan ke pack anda tetapi menggunakan ❤️ sebagai emoji.\
\n\n.kang [emoji] [nomor]\
\nPenggunaan: Curi stiker/gambar ke pack yang ditentukan dan menggunakan emoji yang Anda pilih.\
\n\n.stkrinfo\
\nPenggunaan: Mendapat info tentang pack stiker.\
\n\n.getsticker\
\nPenggunaan: balas stiker untuk mendapatkan file 'PNG' stiker."
    }
)
