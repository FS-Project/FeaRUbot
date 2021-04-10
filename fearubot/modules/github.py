# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

import os
import time
from datetime import datetime

import aiohttp
from github import Github

from fearubot import CMD_HELP, GIT_REPO_NAME, GITHUB_ACCESS_TOKEN, bot
from fearubot.events import register

GIT_TEMP_DIR = "/FeRuBoT/temp/"


@register(outgoing=True, pattern=r".git (.*)")
async def github(event):
    username = event.pattern_match.group(1)
    URL = f"https://api.github.com/users/{username}"
    await event.get_chat()
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as request:
            if request.status == 404:
                return await event.reply(f"{username} tidak ditemukan")

            result = await request.json()

            url = result.get("html_url", None)
            name = result.get("name", None)
            company = result.get("company", None)
            bio = result.get("bio", None)
            created_at = result.get("created_at", "Not Found")

            REPLY = (
                f"Info Akun GitHub `{username}`\n"
                f"Nama Pengguna : `{name}`\n"
                f"Bio           : `{bio}`\n"
                f"URL           : {url}\n"
                f"Perusahaan    : `{company}`\n"
                f"Dibuat pada   : `{created_at}`\n"
                f"Info lainnya  : [Disini](https://api.github.com/users/{username}/events/public)"
            )

            if not result.get("repos_url", None):
                return await event.edit(REPLY)
            async with session.get(result.get("repos_url", None)) as request:
                result = request.json
                if request.status == 404:
                    return await event.edit(REPLY)

                result = await request.json()

                REPLY += "\nRepos:\n"

                for nr in range(len(result)):
                    REPLY += f"[{result[nr].get('name', None)}]({result[nr].get('html_url', None)})\n"

                await event.edit(REPLY)


@register(outgoing=True, pattern="^.commit(?: |$)(.*)")
async def download(event):
    if event.fwd_from:
        return
    if GITHUB_ACCESS_TOKEN is None:
        await event.edit("Harap TAMBAHKAN Token Akses yang Sesuai dari github.com")
        return
    if GIT_REPO_NAME is None:
        await event.edit("Harap TAMBAHKAN Nama Repo Github yang Benar dari userbot Anda")
        return
    mone = await event.reply("Prosesss...")
    if not os.path.isdir(GIT_TEMP_DIR):
        os.makedirs(GIT_TEMP_DIR)
    start = datetime.now()
    reply_message = await event.get_reply_message()
    try:
        time.time()
        print("Downloading to TEMP directory")
        downloaded_file_name = await bot.download_media(
            reply_message.media, GIT_TEMP_DIR
        )
    except Exception as e:
        await mone.edit(str(e))
    else:
        end = datetime.now()
        ms = (end - start).seconds
        await event.delete()
        await mone.edit(
            "Diunduh ke `{}` dalam {} detik.".format(downloaded_file_name, ms)
        )
        await mone.edit("Committing to Github....")
        await git_commit(downloaded_file_name, mone)


async def git_commit(file_name, mone):
    content_list = []
    access_token = GITHUB_ACCESS_TOKEN
    g = Github(access_token)
    file = open(file_name, "r", encoding="utf-8")
    commit_data = file.read()
    repo = g.get_repo(GIT_REPO_NAME)
    print(repo.name)
    create_file = True
    contents = repo.get_contents("")
    for content_file in contents:
        content_list.append(str(content_file))
        print(content_file)
    for i in content_list:
        create_file = True
        if i == 'ContentFile(path="' + file_name + '")':
            return await mone.edit("`File Sudah Ada`")
            create_file = False
    file_name = "fearubot/modules/" + file_name
    if create_file:
        file_name = file_name.replace(GIT_TEMP_DIR, "")
        print(file_name)
        try:
            repo.create_file(
                file_name, "Uploaded New Plugin", commit_data, branch="master"
            )
            print("Committed File")
            ccess = GIT_REPO_NAME
            ccess = ccess.strip()
            await mone.edit(
                f"Commited On Your Github Repo\n\n[Your Modules](https://github.com/{ccess}/tree/master/userbot/modules/)"
            )
        except BaseException:
            print("Cannot Create Plugin")
            await mone.edit("Tidak Dapat Mengunggah Plugin")
    else:
        return await mone.edit("Committed Suicide")


CMD_HELP.update(
    {
        "github": ".git <namapengguna>"
        "\nPenggunaan: Seperti .whois tetapi untuk nama pengguna GitHub."
        "\n\n.commit <balas file>"
        "\nPenggunaan: Pengunggah File ke GITHUB untuk userbot. Otomatisasi Heroku harus Diaktifkan."
    }
)
