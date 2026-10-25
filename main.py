import asyncio
import importlib
import os
from pathlib import Path

from core.bot import bot
from core.userbot import userbot
from core.call import call
from database.db import init_db, close_db
from utils.cleanup import start_cleanup_task
import config

# ---------------------------------------------------------------------------
# cookies.txt dari Config Var YT_COOKIES (Heroku)
# Masalah umum: kolom Netscape harus dipisah TAB, tapi kalau di-paste lewat
# dashboard Heroku TAB sering berubah jadi spasi / baris jadi satu. Di sini
# format itu dipulihkan otomatis, lalu divalidasi dan dilaporkan ke log.
# ---------------------------------------------------------------------------
def _write_cookies_from_env():
    raw = os.environ.get("YT_COOKIES")
    if not raw:
        print("🍪 YT_COOKIES tidak diisi -> yt-dlp jalan tanpa cookies.")
        return

    raw = raw.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n").strip()
    lines_out, valid = ["# Netscape HTTP Cookie File"], 0
    names = set()
    for line in raw.split("\n"):
        s = line.strip()
        if not s or (s.startswith("#") and not s.startswith("#HttpOnly_")):
            continue
        parts = s.split("\t") if s.count("\t") >= 6 else s.split(None, 6)
        if len(parts) >= 7:
            parts = parts[:6] + [" ".join(parts[6:]) if "\t" not in s else parts[6]]
            lines_out.append("\t".join(p.strip() for p in parts))
            valid += 1
            names.add(parts[5].strip())

    with open("cookies.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines_out) + "\n")

    key = {"SID", "HSID", "SSID", "APISID", "SAPISID", "__Secure-3PSID", "LOGIN_INFO"}
    print(f"🍪 cookies.txt dibuat: {valid} cookie valid. Cookie login ditemukan: "
          f"{sorted(key & names) or 'TIDAK ADA (belum login / format rusak)'}")
    if valid == 0:
        print("⚠️ YT_COOKIES terisi tapi tidak ada baris cookie yang valid. Ekspor ulang dalam format Netscape.")

_write_cookies_from_env()


def _print_diagnostics():
    import shutil
    try:
        import yt_dlp
        ytv = yt_dlp.version.__version__
    except Exception as e:
        ytv = f"ERROR {e}"
    print(f"🔎 yt-dlp={ytv} | deno={shutil.which('deno')} | node={shutil.which('node')} | "
          f"ffmpeg={shutil.which('ffmpeg')} | ffprobe={shutil.which('ffprobe')}")
    try:
        import yt_dlp_ejs  # noqa: F401
        print("🔎 yt-dlp-ejs: terpasang")
    except Exception:
        print("⚠️ yt-dlp-ejs TIDAK terpasang (tambahkan `yt-dlp[default]` di requirements.txt)")
    if not (shutil.which("deno") or shutil.which("node")):
        print("⚠️ Tidak ada JS runtime (deno/node) di PATH -> YouTube akan gagal 'format not available'.")
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print("⚠️ ffmpeg/ffprobe tidak ditemukan -> konversi mp3 & play akan gagal. Pasang buildpack ffmpeg.")

_print_diagnostics()


async def load_plugins():
    path = Path("plugins")
    for file in path.rglob("*.py"):
        if not file.name.startswith("__"):
            module_name = str(file).replace("/", ".").replace("\\", ".")[:-3]
            importlib.import_module(module_name)
            print(f"✅ Plugin dimuat: {module_name}")

async def main():
    os.makedirs("downloads", exist_ok=True)

    print("Mempersiapkan Database...")
    await init_db()
    
    print("Menghidupkan Bot & Userbot...")
    await bot.start(bot_token=config.BOT_TOKEN)
    await userbot.start()

    # Paksa Telethon memuat & menyimpan cache entity semua chat yang sudah
    # diikuti userbot. Tanpa ini, userbot bisa gagal dengan
    # "Could not find the input entity" saat mengirim pesan/join VC di
    # sebuah grup yang belum pernah mengirim update apa pun ke sesi ini
    # sejak login (umum terjadi pada sesi yang baru dibuat).
    print("Menyinkronkan daftar grup userbot...")
    await userbot.get_dialogs()
    
    print("Memuat Modul dan Navigasi...")
    await load_plugins()
    
    print("Mengaktifkan Sistem PyTgCalls...")
    await call.start()

    # Tugas latar belakang: bersihkan file download yatim tiap 1 jam
    asyncio.create_task(start_cleanup_task())
    
    print("🚀 MusicBot Professional Berhasil Berjalan!")
    try:
        await asyncio.gather(
            bot.run_until_disconnected(),
            userbot.run_until_disconnected()
        )
    finally:
        await close_db()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 MusicBot dihentikan.")
