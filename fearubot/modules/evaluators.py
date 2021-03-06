# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for executing code and terminal commands from Telegram. """

import asyncio
from os import remove
from sys import executable

from fearubot import BOTLOG, BOTLOG_CHATID, CMD_HELP, USER_TERM_ALIAS
from fearubot.events import register


@register(outgoing=True, pattern="^.eval(?: |$)(.*)")
async def evaluate(query):
    """ For .eval command, evaluates the given Python expression. """
    if query.is_channel and not query.is_group:
        await query.edit("Evaluasi tidak diizinkan di channel.")
        return

    if query.pattern_match.group(1):
        expression = query.pattern_match.group(1)
    else:
        await query.edit("``` Berikan expression untuk dievaluasi. ```")
        return

    if expression in ("userbot.session", "config.env"):
        await query.edit("`Itu operasi yang berbahaya! Tidak diperbolehkan!`")
        return

    try:
        evaluation = str(eval(expression))
        if evaluation:
            if isinstance(evaluation, str):
                if len(evaluation) >= 4096:
                    file = open("output.txt", "w+")
                    file.write(evaluation)
                    file.close()
                    await query.client.send_file(
                        query.chat_id,
                        "output.txt",
                        reply_to=query.id,
                        caption="`Output terlalu besar, dikirim sebagai file`",
                    )
                    remove("output.txt")
                    return
                await query.edit(
                    "**Query    : **\n`"
                    f"{expression}"
                    "`\n**Hasil : **\n`"
                    f"{evaluation}"
                    "`"
                )
        else:
            await query.edit(
                "**Query    : **\n`"
                f"{expression}"
                "`\n**Hasil : **\n`Tidak Ada Hasil yang Dikembalikan/Salah`"
            )
    except Exception as err:
        await query.edit(
            "**Query: **\n`" f"{expression}" "`\n**Exception: **\n" f"`{err}`"
        )

    if BOTLOG:
        await query.client.send_message(
            BOTLOG_CHATID, f"Eval query {expression} berhasil dijalankan"
        )


@register(outgoing=True, pattern=r"^.exec(?: |$)([\s\S]*)")
async def run(run_q):
    """ For .exec command, which executes the dynamically created program """
    code = run_q.pattern_match.group(1)

    if run_q.is_channel and not run_q.is_group:
        await run_q.edit("`Exec tidak diizinkan di channel!`")
        return

    if not code:
        await run_q.edit(
            "``` At least a variable is required to \
execute. Use .help exec for an example.```"
        )
        return

    if code in ("userbot.session", "config.env", "env"):
        await run_q.edit("`Itu operasi yang berbahaya! Tidak diperbolehkan!`")
        return

    if len(code.splitlines()) <= 5:
        codepre = code
    else:
        clines = code.splitlines()
        codepre = (
            clines[0] + "\n" + clines[1] + "\n" + clines[2] + "\n" + clines[3] + "..."
        )

    command = "".join(f"\n {l}" for l in code.split("\n.strip()"))
    process = await asyncio.create_subprocess_exec(
        executable,
        "-c",
        command.strip(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if result:
        if len(result) > 4096:
            file = open("output.txt", "w+")
            file.write(result)
            file.close()
            await run_q.client.send_file(
                run_q.chat_id,
                "output.txt",
                reply_to=run_q.id,
                caption="`Output terlalu besar, dikirim sebagai file`",
            )
            remove("output.txt")
            return
        await run_q.edit(
            "**Query: **\n`" f"{codepre}" "`\n**Hasil: **\n`" f"{result}" "`"
        )
    else:
        await run_q.edit(
            "**Query: **\n`" f"{codepre}" "`\n**Hasil: **\n`No Result Returned/False`"
        )

    if BOTLOG:
        await run_q.client.send_message(
            BOTLOG_CHATID, "Exec query " + codepre + " Berhasil dijalankan"
        )


@register(outgoing=True, pattern="^.term(?: |$)(.*)")
async def terminal_runner(term):
    """ For .term command, runs bash commands and scripts on your server. """
    curruser = USER_TERM_ALIAS
    command = term.pattern_match.group(1)
    try:
        from os import geteuid

        uid = geteuid()
    except ImportError:
        uid = "This ain't it chief!"

    if term.is_channel and not term.is_group:
        await term.edit("`Perintah istilah tidak diizinkan di channel!`")
        return

    if not command:
        await term.edit(
            "``` Give a command or use .help term for \
            an example.```"
        )
        return

    if command in ("userbot.session", "config.env", "env", "$", "$*", "echo"):
        await term.edit("`Itu operasi yang berbahaya! Tidak diperbolehkan!`")
        return

    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if len(result) > 4096:
        output = open("output.txt", "w+")
        output.write(result)
        output.close()
        await term.client.send_file(
            term.chat_id,
            "output.txt",
            reply_to=term.id,
            caption="`Output terlalu besar, dikirim sebagai file``",
        )
        remove("output.txt")
        return

    if uid == 0:
        await term.edit("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await term.edit("`" f"{curruser}:~$ {command}" f"\n{result}" "`")

    if BOTLOG:
        await term.client.send_message(
            BOTLOG_CHATID,
            "Terminal Command " + command + " dieksekusi dengan sukses",
        )


CMD_HELP.update({"eval": ".eval 2 + 3\nPenggunaan: Evaluasi mini-expressions."})
CMD_HELP.update({"exec": ".exec print('hello')\nPenggunaan: Jalankan skrip python kecil."})
CMD_HELP.update(
    {"term": ".term ls\nPenggunaan: Jalankan perintah dan skrip bash di server Anda."}
)
