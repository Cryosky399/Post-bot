import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from keep_alive import keep_alive

# --- Sozlamalar ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_TELEGRAM_BOT_TOKEN_HERE")

# --- Yordamchi funksiyalar ---
url_andozasi = re.compile(r"(https?://\S+)")

def satrni_havolaga_aylantir(satr: str) -> str:
    satr = satr.strip()
    if not satr:
        return ""

    md = re.match(r"^\s*\[(?P<title>[^\]]+)\]\((?P<url>https?://[^\s)]+)\)\s*$", satr)
    if md:
        nomi = md.group("title").strip()
        url = md.group("url").strip()
        return f"<a href=\"{url}\">{types.utils.escape_html(nomi)}</a>"

    if "|" in satr:
        chap, ong = satr.split("|", 1)
        nomi = chap.strip()
        url = ong.strip()
        return f"<a href=\"{url}\">{types.utils.escape_html(nomi)}</a>" if url_andozasi.search(url) else ""
    if " - " in satr:
        chap, ong = satr.split(" - ", 1)
        nomi = chap.strip()
        url = ong.strip()
        return f"<a href=\"{url}\">{types.utils.escape_html(nomi)}</a>" if url_andozasi.search(url) else ""
    if " : " in satr:
        chap, ong = satr.split(" : ", 1)
        nomi = chap.strip()
        url = ong.strip()
        return f"<a href=\"{url}\">{types.utils.escape_html(nomi)}</a>" if url_andozasi.search(url) else ""

    mos = url_andozasi.search(satr)
    if mos:
        url = mos.group(1)
        nomi = (satr[: mos.start()] + satr[mos.end():]).strip()
        if not nomi:
            return ""
        return f"<a href=\"{url}\">{types.utils.escape_html(nomi)}</a>"
    return ""

def matnni_havolalarga_aylantir(matn: str) -> str:
    natija_qatorlar = []
    for satr in matn.splitlines():
        havola = satrni_havolaga_aylantir(satr)
        if havola:
            natija_qatorlar.append(f"• {havola}")
    return "\n".join(natija_qatorlar).strip()

# --- Bot ---
if not BOT_TOKEN or BOT_TOKEN == "PASTE_TELEGRAM_BOT_TOKEN_HERE":
    raise SystemExit("Iltimos, BOT_TOKEN ni sozlang.")

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start", "help"])
async def boshlash(msg: types.Message):
    matn = (
        "Salom! Men matnni ‘ko'k yozuv’ (matn ichidagi link) holatiga aylantiradigan botman.\n\n"
        "Qanday ishlatish:\n"
        "1) Bitta:  Naruto | https://t.me/c/1963863623/612\n"
        "2) Ko'p qator: \n"
        "   One Piece | https://t.me/username/5678\n"
        "   Bleach - https://t.me/c/1963863623/91011\n\n"
        "Men sizga tugmasiz, postsiz — faqat matn ichida klik qilinadigan link bilan javob qaytaraman."
    )
    await msg.answer(matn)

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def matn_qabul_qilish(msg: types.Message):
    kirish = msg.text.strip()
    tayyor = matnni_havolalarga_aylantir(kirish)
    if not tayyor:
        await msg.reply(
            "Iltimos, matn va link yuboring.\nMasalan: Naruto | https://t.me/c/1963863623/612",
            disable_web_page_preview=True,
        )
        return
    await msg.answer(tayyor, disable_web_page_preview=True)

# KeepAlive server
keep_alive()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
