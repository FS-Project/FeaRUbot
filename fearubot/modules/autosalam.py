# Yang punya mohon izin

from time import sleep
from platform import uname
from fearubot import ALIVE_NAME, CMD_HELP
from fearubot.events import register

@register(outgoing=True, pattern='^ass(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("*Assalamualaikum.....*")
# Owner @Si_Dian


@register(outgoing=True, pattern='^Ass(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("*Assalamualaikum.....*")
# Owner @Si_Dian


@register(outgoing=True, pattern='^waa(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("*Waallaikumsalam......*")
# Owner @Si_Dian


@register(outgoing=True, pattern='^Waa(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)

    await typew.edit("*Waallaikumsalam.....*")
# Owner @Si_Dian


CMD_HELP.update({
    "auto salam":
    "`Ass`\
\nPenggunaan: Ketik `Ass` dimana saja untuk Memberi salam.\
\n\n`Waa`\
\nPenggunaan: Ketik `Waa` dimana saja untuk Menjawab Salam."
})
