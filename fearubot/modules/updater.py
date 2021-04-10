# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
# credits to @AvinashReddy3108
#
"""
This module updates the userbot based on upstream revision
"""

import asyncio
import sys
from os import environ, execle, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from fearubot import (
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    HEROKU_API_KEY,
    HEROKU_APP_NAME,
    UPDATER_ALIAS,
    UPSTREAM_REPO_BRANCH,
    UPSTREAM_REPO_URL,
)
from fearubot.events import register

requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "%h/%m/%t"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n"
        )
    return ch_log


async def update_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is not None:
        import heroku3

        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if HEROKU_APP_NAME is None:
            await event.edit(
                "**Harap isi variabel HEROKU_APP_NAME"
                "untuk dapat menerapkan perubahan terbaru.**"
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await event.edit(
                f"{txt}\n*Kredensial Heroku tidak valid untuk men-deploy userbot.*"
            )
            return repo.__del__()
        await event.edit("*Sedang proses, harap tunggu...*")
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except GitCommandError as error:
            await event.edit(f"{txt}\nIni adalah log **Error**:\n{error}")
            return repo.__del__()
        await event.edit("**Update Berhasil**☑️!\n" "**Sedang Mulai Ulang, Harap Tunggu...**")

        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID, "#UPDATE \n" "**UserBot FeaRUbot Anda sudah ter-update, yaaay**"
            )

    else:
        await event.edit("*Harap set variabel HEROKU_API_KEY.*")
    return


async def update(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await update_requirements()
    await event.edit(
        "*Update Berhasil☑️!\n" "Sedang Mulai Ulang, Harap Tunggu...*"
    )

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#*UPDATE* \n" "*Userbot FeaRUbot Anda sudah ter-update, yaaay*"
        )

    # Spin a new instance of bot
    args = [sys.executable, "-m", "userbot"]
    execle(sys.executable, *args, environ)
    return


@register(outgoing=True, pattern=r"^.update(?: |$)(now|deploy)?")
async def upstream(event):
    "For .update command, check if the bot is up to date, update if specified"
    await event.edit("**Memeriksa update, harap tunggu....**")
    conf = event.pattern_match.group(1)
    off_repo = UPSTREAM_REPO_URL
    force_update = False
    try:
        txt = "**Ups.. Updater tidak dapat melanjutkan karena "
        txt += "*terjadi beberapa masalah**\n\n**LOGTRACE:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\ndirectory {error} tidak ditemukan")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\nGagal! {error}")
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(
                f"**Sayangnya, direktori {error} tampaknya bukan repositori git tapi**."
                "\n**bisa memperbaikinya dengan memperbarui paksa userbot menggunakan .update now.**"
            )
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("main", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)

    ac_br = repo.active_branch.name
    if ac_br != UPSTREAM_REPO_BRANCH:
        await event.edit(
            "**[UPDATER]:**\n"
            f"**Sepertinya Anda menggunakan custom branch Anda sendiri ({ac_br}). "
            "dalam hal ini, Updater tidak dapat mengidentifikasi "
            "branch mana yang akan digabungkan. "
            "silakan gunakan branch resmi**"
        )
        return repo.__del__()
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")

    if changelog == "" and force_update is False:
        await event.edit(
            f"\n**FeaRUbot anda sudah terbaru, dengan branch** **{UPSTREAM_REPO_BRANCH}**\n"
        )
        return repo.__del__()

    if conf is None and force_update is False:
        changelog_str = (
            f"**Update tersedia untuk [{ac_br}]:\n\nCHANGELOG:**\n`{changelog}`"
        )
        if len(changelog_str) > 4096:
            await event.edit("**Changelog terlalu besar, buka file untuk melihatnya.**")
            file = open("output.txt", "w+")
            file.write(changelog_str)
            file.close()
            await event.client.send_file(
                event.chat_id,
                "output.txt",
                reply_to=event.id,
            )
            remove("output.txt")
        else:
            await event.edit(changelog_str)
        return await event.respond("**Lakukan .update now / .update deploy untuk update**")

    if force_update:
        await event.edit(
            "**Memperbarui FeaRUbot secara paksa ke versi terbaru, harap tunggu...**"
        )
    else:
        await event.edit("**Sedang update FeaRUbot, Harap Tunggu....**")
    if conf == "now":
        await update(event, repo, ups_rem, ac_br)
    elif conf == "deploy":
        await deploy(event, repo, ups_rem, ac_br, txt)
    return


CMD_HELP.update(
    {
        "update": ".update"
        "\nPenggunaan: Memeriksa apakah ada update pada FeaRUbot dan menampilkan changelog jika ada update."
        "\n\n.update now"
        "\nPenggunaan: Perbarui FeaRUbot Anda, jika ada pembaruan di repositori FeaRUbot Anda."
        "\n\n.update deploy"
        "\nPenggunaan: Deploy FeaRUbot Anda di heroku, jika ada pembaruan di repositori FeaRUbot Anda."
    }
)
