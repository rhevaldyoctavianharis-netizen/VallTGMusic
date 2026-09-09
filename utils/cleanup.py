import asyncio
import os
import time
from database.db import get_all_referenced_media_files

DOWNLOAD_DIR = "downloads"
MAX_AGE_SECONDS = 6 * 3600  # jangan sentuh file yang masih segar (mungkin sedang diproses)
CHECK_INTERVAL = 3600       # jalan tiap 1 jam


async def _cleanup_once():
    if not os.path.isdir(DOWNLOAD_DIR):
        return

    referenced = await get_all_referenced_media_files()
    now = time.time()
    removed = 0

    for name in await asyncio.to_thread(os.listdir, DOWNLOAD_DIR):
        path = os.path.join(DOWNLOAD_DIR, name)
        if path in referenced:
            continue
        try:
            stat = await asyncio.to_thread(os.stat, path)
        except FileNotFoundError:
            continue
        if now - stat.st_mtime < MAX_AGE_SECONDS:
            continue  # masih baru, biarkan (bisa jadi baru saja didownload)
        try:
            await asyncio.to_thread(os.remove, path)
            removed += 1
        except Exception:
            pass

    if removed:
        print(f"🧹 Cleanup: {removed} file yatim di '{DOWNLOAD_DIR}/' dihapus.")


async def start_cleanup_task():
    """
    Jaring pengaman: kalau bot pernah crash di tengah proses (sehingga file
    hasil download gagal dihapus oleh alur normal), tugas ini yang secara
    berkala membersihkan file-file lama yang sudah tidak direferensikan
    oleh stream/antrean manapun. Berjalan di background, tidak mengganggu
    proses lain.
    """
    while True:
        try:
            await _cleanup_once()
        except Exception as e:
            print(f"Cleanup task error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
