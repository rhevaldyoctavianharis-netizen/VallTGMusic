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
