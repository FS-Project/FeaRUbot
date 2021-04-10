# INFO : ini merupakan copy source code dari repo one4ubot, dan sudah mendapatkan izin dari pemilik.
# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Port to UserBot by @MoveAngel

from covid import Covid

from fearubot import CMD_HELP
from fearubot.events import register


@register(outgoing=True, pattern="^.covid (.*)")
async def corona(event):
    await event.edit("`Proses...`")
    country = event.pattern_match.group(1)
    covid = Covid(source="worldometers")
    try:
        country_data = covid.get_status_by_country_name(country)
        output_text = (
            f"*Terkonfirmasi*   : {format_integer(country_data['confirmed'])}\n"
            + f"*Atif*      : {format_integer(country_data['active'])}`\n"
            + f"*Meninggal*      : {format_integer(country_data['deaths'])}`\n"
            + f"*Sembuh*   : {format_integer(country_data['recovered'])}`\n\n"
            + f"*Kasus aktif baru*   : {format_integer(country_data['new_cases'])}`\n"
            + f"*Kasus meninggal baru*  : {format_integer(country_data['new_deaths'])}`\n"
            + f"*Total Tes*  : {format_integer(country_data['total_tests'])}`\n\n"
            + f"*Data disediakan oleh* [Worldometer](https://www.worldometers.info/coronavirus/country/{country})"
        )
        await event.edit(f"*Info Virus Corona di {country}:\n\n{output_text}*")
    except ValueError:
        await event.edit(
            f"*Tidak ada informasi yang ditemukan untuk: {country}!\nPeriksa ejaan Anda dan coba lagi*."
        )


def format_integer(number, thousand_separator="."):
    def reverse(string):
        string = "".join(reversed(string))
        return string

    s = reverse(str(number))
    count = 0
    result = ""
    for char in s:
        count = count + 1
        if count % 3 == 0:
            if len(s) == count:
                result = char + result
            else:
                result = thousand_separator + char + result
        else:
            result = char + result
    return result


CMD_HELP.update(
    {
        "covid": ".covid <negara>"
        "\n*Penggunaan: Dapatkan informasi tentang data covid-19 di negara Anda.*\n"
    }
)
