import aiosqlite
import asyncio
import config
from typing import Optional

DB_NAME = "bot_brain.db"

# --- KONEKSI PERSISTEN (dipakai bersama, bukan buka-tutup tiap query) ---
# Sebelumnya setiap fungsi membuka koneksi SQLite baru sendiri-sendiri.
# Ini sangat boros karena progress_bar_updater() saja memanggil DB
# beberapa kali per detik untuk SETIAP grup yang sedang streaming.
# Sekarang cukup satu koneksi yang dipakai ulang selama proses berjalan,
# dengan WAL mode agar baca/tulis tidak saling mengunci.
_conn: Optional[aiosqlite.Connection] = None
_lock = asyncio.Lock()  # melindungi operasi read-modify-write agar tidak race condition

# Whitelist kolom yang boleh diubah lewat update_user() -- mencegah
# kemungkinan SQL injection dari nama kolom yang sebelumnya di-interpolasi langsung.
_ALLOWED_USER_FIELDS = {"role", "status", "points", "vip_until", "trial_claimed", "dl_count", "username"}


def _db() -> aiosqlite.Connection:
    if _conn is None:
        raise RuntimeError("Database belum diinisialisasi. Panggil init_db() terlebih dahulu.")
    return _conn


async def init_db():
    global _conn
    _conn = await aiosqlite.connect(DB_NAME)
    # WAL + synchronous=NORMAL: jauh lebih ringan untuk beban baca/tulis
    # yang sering (progress bar, antrean) tanpa mengorbankan keamanan data.
    await _conn.execute("PRAGMA journal_mode=WAL")
    await _conn.execute("PRAGMA synchronous=NORMAL")

    await _conn.execute("""CREATE TABLE IF NOT EXISTS active_streams (
        chat_id INTEGER PRIMARY KEY, status TEXT, current_media TEXT,
        is_loop INTEGER DEFAULT 0, duration INTEGER DEFAULT 0, current_time INTEGER DEFAULT 0)""")

    await _conn.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, role TEXT DEFAULT 'user', status TEXT DEFAULT 'active')""")

    await _conn.execute("""CREATE TABLE IF NOT EXISTS stream_queues (
        id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, title TEXT,
        role TEXT, media_file TEXT, is_video INTEGER DEFAULT 0)""")

    await _conn.execute("""CREATE TABLE IF NOT EXISTS banned_groups (
        chat_id INTEGER PRIMARY KEY)""")

    await _conn.execute("""CREATE TABLE IF NOT EXISTS stream_roles (
        chat_id INTEGER PRIMARY KEY, role TEXT)""")

    for stmt in (
        "ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN vip_until INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN trial_claimed INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN dl_count INTEGER DEFAULT 0",
    ):
        try:
            await _conn.execute(stmt)
        except Exception:
            pass

    # Index untuk mempercepat query queue per chat (dipakai berulang kali)
    await _conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_chat ON stream_queues(chat_id)")

    if config.ADMIN_ID:
        await _conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, role, status, points, vip_until) VALUES (?, ?, 'admin', 'active', 0, 0)",
            (config.ADMIN_ID, "Owner"),
        )
    await _conn.commit()


async def close_db():
    """Tutup koneksi DB dengan rapi saat bot dimatikan."""
    global _conn
    if _conn is not None:
        await _conn.close()
        _conn = None


async def ban_group(chat_id):
    db = _db()
    await db.execute("INSERT OR IGNORE INTO banned_groups (chat_id) VALUES (?)", (chat_id,))
    await db.commit()


async def unban_group(chat_id):
    db = _db()
    await db.execute("DELETE FROM banned_groups WHERE chat_id=?", (chat_id,))
    await db.commit()


async def is_group_banned(chat_id):
    db = _db()
    async with db.execute("SELECT chat_id FROM banned_groups WHERE chat_id=?", (chat_id,)) as c:
        res = await c.fetchone()
        return res is not None


async def get_all_banned_groups():
    db = _db()
    async with db.execute("SELECT chat_id FROM banned_groups") as c:
        return await c.fetchall()


async def add_or_get_user(user_id, username, referrer_id=None):
    db = _db()
    async with _lock:
        async with db.execute("SELECT role, status FROM users WHERE user_id=?", (user_id,)) as c:
            u = await c.fetchone()
        if not u:
            await db.execute(
                "INSERT INTO users (user_id, username, points, vip_until, trial_claimed, dl_count) VALUES (?, ?, 0, 0, 0, 0)",
                (user_id, username),
            )
            if referrer_id and referrer_id != user_id:
                await db.execute("UPDATE users SET points = points + 1 WHERE user_id=?", (referrer_id,))
            await db.commit()
            return "user", "active", True
        return u[0], u[1], False


async def get_user_full(user_id):
    db = _db()
    async with db.execute(
        "SELECT role, status, points, vip_until, username, trial_claimed, dl_count FROM users WHERE user_id=?",
        (user_id,),
    ) as c:
        return await c.fetchone()


async def update_user(user_id, field, value):
    if field not in _ALLOWED_USER_FIELDS:
        raise ValueError(f"Field '{field}' tidak diizinkan untuk diubah.")
    db = _db()
    await db.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
    await db.commit()


async def try_purchase_vip(user_id, cost, duration_sec):
    """
    Potong poin & aktifkan VIP secara ATOMIK dalam satu statement SQL,
    supaya dua klik tombol beli yang hampir bersamaan tidak bisa
    sama-sama lolos dengan poin yang sama (race condition pada versi lama).
    Mengembalikan (berhasil: bool, sisa_poin: int)
    """
    import time
    db = _db()
    async with _lock:
        vip_until = int(time.time()) + duration_sec
        cursor = await db.execute(
            "UPDATE users SET points = points - ?, role = 'vip', vip_until = ? WHERE user_id = ? AND points >= ?",
            (cost, vip_until, user_id, cost),
        )
        await db.commit()
        success = cursor.rowcount > 0
        async with db.execute("SELECT points FROM users WHERE user_id=?", (user_id,)) as c:
            row = await c.fetchone()
        return success, (row[0] if row else 0)


async def increment_dl_count(user_id):
    db = _db()
    await db.execute("UPDATE users SET dl_count = dl_count + 1 WHERE user_id=?", (user_id,))
    await db.commit()


async def update_stream(chat_id, status, media="", is_loop=0, duration=0, current_time=0):
    db = _db()
    await db.execute(
        "INSERT OR REPLACE INTO active_streams VALUES (?,?,?,?,?,?)",
        (chat_id, status, media, is_loop, duration, current_time),
    )
    await db.commit()


async def get_stream(chat_id):
    db = _db()
    async with db.execute("SELECT * FROM active_streams WHERE chat_id=?", (chat_id,)) as c:
        return await c.fetchone()


async def update_time(chat_id, current_time):
    async with _lock:
        stream = await get_stream(chat_id)
        if stream:
            await update_stream(chat_id, stream[1], stream[2], stream[3], stream[4], current_time)


async def toggle_loop(chat_id):
    async with _lock:
        stream = await get_stream(chat_id)
        if stream:
            new_loop = 0 if stream[3] == 1 else 1
            await update_stream(chat_id, stream[1], stream[2], new_loop, stream[4], stream[5])
            return new_loop
        return 0


async def set_stream_role(chat_id, role):
    db = _db()
    await db.execute("INSERT OR REPLACE INTO stream_roles (chat_id, role) VALUES (?, ?)", (chat_id, role))
    await db.commit()


async def get_replaceable_user_stream():
    db = _db()
    async with db.execute("""
        SELECT a.chat_id FROM active_streams a
        JOIN stream_roles r ON a.chat_id = r.chat_id
        WHERE a.status IN ('playing', 'paused', 'downloading') AND r.role = 'user'
        LIMIT 1
    """) as c:
        res = await c.fetchone()
        return res[0] if res else None


async def get_global_stream_count():
    db = _db()
    async with db.execute("SELECT COUNT(*) FROM active_streams WHERE status IN ('playing', 'paused', 'downloading')") as c:
        res = await c.fetchone()
        return res[0] if res else 0


async def get_all_active_streams(limit=5, offset=0):
    db = _db()
    async with db.execute(
        "SELECT chat_id, current_media, status FROM active_streams WHERE status IN ('playing', 'paused', 'downloading') LIMIT ? OFFSET ?",
        (limit, offset),
    ) as c:
        streams = await c.fetchall()
    async with db.execute("SELECT COUNT(*) FROM active_streams WHERE status IN ('playing', 'paused', 'downloading')") as c:
        total = await c.fetchone()
    return streams, (total[0] if total else 0)


async def get_all_referenced_media_files():
    """
    Kumpulan semua path file media yang MASIH dipakai (sedang diputar
    atau menunggu di antrean). Dipakai oleh tugas pembersih file yatim
    supaya tidak menghapus file yang ternyata masih dibutuhkan.
    """
    db = _db()
    files = set()
    async with db.execute("SELECT current_media FROM active_streams WHERE current_media != ''") as c:
        async for row in c:
            files.add(row[0])
    async with db.execute("SELECT media_file FROM stream_queues") as c:
        async for row in c:
            files.add(row[0])
    return files


async def add_to_queue(chat_id, title, role, media_file, is_video):
    db = _db()
    await db.execute(
        "INSERT INTO stream_queues (chat_id, title, role, media_file, is_video) VALUES (?, ?, ?, ?, ?)",
        (chat_id, title, role, media_file, int(is_video)),
    )
    await db.commit()


async def get_queue(chat_id):
    db = _db()
    async with db.execute(
        "SELECT id, title, role, media_file, is_video FROM stream_queues WHERE chat_id=? ORDER BY id ASC", (chat_id,)
    ) as c:
        return await c.fetchall()


async def remove_from_queue(queue_id):
    db = _db()
    await db.execute("DELETE FROM stream_queues WHERE id=?", (queue_id,))
    await db.commit()


async def clear_queue(chat_id):
    db = _db()
    await db.execute("DELETE FROM stream_queues WHERE chat_id=?", (chat_id,))
    await db.commit()


async def pop_queue(chat_id):
    async with _lock:
        db = _db()
        async with db.execute(
            "SELECT id, title, role, media_file, is_video FROM stream_queues WHERE chat_id=? ORDER BY id ASC LIMIT 1",
            (chat_id,),
        ) as c:
            item = await c.fetchone()
        if item:
            await db.execute("DELETE FROM stream_queues WHERE id=?", (item[0],))
            await db.commit()
            return item
        return None


async def delete_user(user_id):
    db = _db()
    await db.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    await db.commit()


async def get_all_users():
    db = _db()
    async with db.execute("SELECT user_id, username, role, status FROM users") as c:
        return await c.fetchall()
