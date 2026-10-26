from telethon import events, Button
from core.bot import bot
from core.call import call 
from utils.streamer import download_and_play, search_youtube
from utils.inline import stream_controls, search_buttons, film_buttons, queue_buttons, listplay_buttons
from utils.media import get_duration, get_thumbnail, safe_delete
from utils.panel import send_stream_panel, get_duration_smart
from database.db import get_stream, update_stream, update_time, add_to_queue, get_queue, remove_from_queue, clear_queue, get_user_full, increment_dl_count, get_global_stream_count, get_all_active_streams, set_stream_role, get_replaceable_user_stream
from utils.checker import is_user_allowed
import asyncio
import html
import aiohttp
import os
import re
import config

SEARCH_CACHE = {}
FILM_CACHE = {} 
FORMAT_CACHE = {}

# API LK21 LOKAL (Ganti port jika node.js Anda berjalan di port berbeda)
LK21_API_URL = "http://localhost:3000" 

background_tasks = set()

def is_url(text): return re.match(r'^https?://', text)

def parse_time(time_val):
    if isinstance(time_val, (int, float)): return int(time_val)
    if isinstance(time_val, str):
        if ":" in time_val:
            p = time_val.split(":")
            try:
                if len(p) == 2: return int(p[0]) * 60 + int(float(p[1]))
                if len(p) == 3: return int(p[0]) * 3600 + int(p[1]) * 60 + int(float(p[2]))
            except: return 0
        try: return int(float(time_val))
        except: return 0
    return 0

# FUNGSI API LK21
async def search_film_api(query):
    results = []
    clean_query = query.replace(" ", "+").lower()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{LK21_API_URL}/search?query={clean_query}", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data if isinstance(data, list) else data.get("result", [])
                    for item in items:
                        movie_id = item.get("id") or item.get("link")
                        title = item.get("title")
                        if movie_id and title:
                            results.append({"title": f"🎬 {title}", "movie_id": movie_id, "is_yt": False})
    except Exception as e: print(f"LK21 API Error: {e}")

    if not results:
        yt_results = await search_youtube(f"{query} full movie", limit=5)
        for res in yt_results:
            if int(res.get('duration', 0)) > 2400:
                results.append({"title": f"📺 {res.get('title')}", "movie_id": res.get('url'), "is_yt": True})
    return results[:5]

async def get_film_stream_url(movie_id):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{LK21_API_URL}/get?id={movie_id}", timeout=15) as watch_resp:
                if watch_resp.status == 200:
                    w_data = await watch_resp.json()
                    stream_url = w_data.get("stream_url")
                    if stream_url: return stream_url
                    
                    providers = w_data.get("providers", [])
                    if providers and isinstance(providers, list):
                        for p in providers:
                            if p.get("url"): return p.get("url")
    except Exception as e: print(f"LK21 Stream Error: {e}")
    return None

# ADMIN DASHBOARD
@bot.on(events.NewMessage(pattern=r'(?i)^/listplay$'))
async def listplay_cmd(event):
    is_allowed, role = await is_user_allowed(event, bot)
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    if role not in ['admin', 'owner', 'vip'] and not is_owner: 
        return await event.respond("❌ Akses Ditolak: Khusus Admin/Owner!")
        
    streams, total = await get_all_active_streams(5, 0)
    if not streams: return await event.respond("ℹ️ Server kosong. Tidak ada grup yang sedang memutar stream.")
        
    total_pages = (total // 5) + (1 if total % 5 != 0 else 0)
    text = f"📊 **DASHBOARD SERVER ({total} Grup Aktif):**\n\n"
    for s in streams: text += f"🔹 **Group ID:** `{s[0]}`\n🎵 **Status:** `{s[2].upper()}`\n\n"
    await event.respond(text, buttons=listplay_buttons(streams, 0, total_pages))

@bot.on(events.NewMessage(pattern=r'(?i)^/listban$'))
async def listban_cmd(event):
    is_allowed, role = await is_user_allowed(event, bot)
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    if role not in ['admin', 'owner'] and not is_owner: 
        return await event.respond("❌ Akses Ditolak: Khusus Admin/Owner!")
        
    from database.db import get_all_banned_groups
    banned = await get_all_banned_groups()
    if not banned: return await event.respond("✅ Server bersih. Tidak ada grup yang di-banned.")
        
    total = len(banned)
    total_pages = (total // 5) + (1 if total % 5 != 0 else 0)
    current_banned = banned[0:5]
    text = f"🚫 **DAFTAR GRUP BANNED ({total} Grup):**\n\n"
    for b in current_banned: text += f"🔹 **Group ID:** `{b[0]}`\n"
        
    from utils.inline import listban_buttons
    await event.respond(text, buttons=listban_buttons(current_banned, 0, total_pages))

# DOWNLOADER
@bot.on(events.NewMessage(pattern=r'(?i)^/dl(?:@\w+)?(?: |$)(.*)'))
async def dl_cmd(event):
    is_allowed, role = await is_user_allowed(event, bot)
    if not is_allowed: return
    
    query = event.pattern_match.group(1).strip()
    if not query or not is_url(query): return await event.respond("⚠️ Gunakan format: `/dl [link youtube/tiktok]`")

    user_id = event.sender_id
    u_data = await get_user_full(user_id)
    dl_count = u_data[6] if u_data and len(u_data) > 6 else 0
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    
    if role == 'user' and dl_count >= 10 and not is_owner:
        return await event.respond("❌ **Limit Tercapai!**\nUser biasa hanya bisa memakai Downloader 10 kali.\n🔥 *Upgrade ke VIP untuk Download Tanpa Batas!*")
        
    msg_ub = await event.respond("⏳ **Mengunduh media...**\n_Sistem memproses permintaan Anda._")
    try:
        from utils.streamer import sync_download
        media_file = await asyncio.to_thread(sync_download, query, role, "audio")
        if media_file.startswith("ERROR:"): return await msg_ub.edit(f"❌ **Gagal!**\n{media_file}")
            
        sisa = "Unlimited" if (role != 'user' or is_owner) else str(9 - dl_count)
        await bot.send_file(event.chat_id, file=media_file, caption=f"✅ **Berhasil Diunduh**\nSisa Kuota Anda: **{sisa}**", reply_to=event.message)
        await msg_ub.delete()
        if role == 'user' and not is_owner: await increment_dl_count(user_id)
        os.remove(media_file)
    except Exception as e: await msg_ub.edit(f"❌ **Kesalahan:** {str(e)}")

# ALUR ANTRIAN & PRIORITAS VIP
async def handle_play_or_queue(event, intent):
    if event.is_private: return await event.respond("❌ Perintah ini hanya untuk di grup.")
    is_allowed, role = await is_user_allowed(event, bot)
    if not is_allowed: return 
    
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    match = event.pattern_match.group(1)
    query = match.strip() if match else ""
    chat_id = event.chat_id
    reply_to_msg = await event.get_reply_message()
    is_media_reply = reply_to_msg and (reply_to_msg.audio or reply_to_msg.video or reply_to_msg.voice)
    
    if not query and not is_media_reply:
        if intent == "queue":
            q_list = await get_queue(chat_id)
            if not q_list: return await event.respond("Kosong! Tidak ada antrean musik saat ini.\n_Gunakan `/queue [link/judul]`._")
            text = "📜 **Daftar Antrean Musik:**\n\n"
            for i, data in enumerate(q_list): text += f"**{i+1}.** `{data[1]}`\n"
            text += "\n*Klik tombol di bawah untuk menghapus lagu dari antrean.*"
            return await event.respond(text, buttons=queue_buttons(q_list))
        else: return await event.respond("⚠️ Gunakan `/play (judul/link)` atau `/queue (judul/link)`.")

    global_streams = await get_global_stream_count()
    check_active = await get_stream(chat_id)
    is_active = check_active and check_active[1] in ["playing", "paused", "downloading"]

    # TEMBOK PERTAHANAN LIMIT 10
    if not is_active and global_streams >= 10:
        if role == 'user' and not is_owner:
            return await event.respond("❌ **Server Penuh!**\nMaksimal 10 grup yang bisa stream bersamaan. Silakan coba lagi nanti atau Upgrade VIP!")
        else:
            replaceable_chat = await get_replaceable_user_stream()
            if replaceable_chat:
                old_stream = await get_stream(replaceable_chat)
                old_queue = await get_queue(replaceable_chat)
                try: await call.leave_call(replaceable_chat)
                except: pass
                await update_stream(replaceable_chat, "stopped", "", 0, 0, 0)
                await clear_queue(replaceable_chat)
                if old_stream and len(old_stream) > 2: await safe_delete(old_stream[2])
                for item in old_queue: await safe_delete(item[3])
                msg = "⚠️ **Maaf musik terpaksa di hentikan karna ada user vip yang menggunakan silahkan tunggu user vip tersebut selesai dengan streamnya lalu play ulang**"
                try: await bot.send_message(replaceable_chat, msg)
                except: pass
            else: return await event.respond("❌ **Server Super Penuh!**\n10 Slot server saat ini sedang dipakai secara eksklusif oleh VIP/Admin lain.")

    if is_active and intent == "play" and role == 'user' and not is_owner:
        intent = "queue"
        await event.respond("⚠️ **Peringatan Level:** User biasa tidak bisa memotong lagu yang sedang menyala.\nPermintaan dialihkan ke **Antrean**.\n_(Upgrade VIP untuk Bypass)_")

    if is_url(query):
        cache_id = f"{chat_id}_{event.sender_id}"
        FORMAT_CACHE[cache_id] = {"query": query, "role": role, "intent": intent}
        btns = [[Button.inline("🎵 Putar Audio", b"fmt_audio"), Button.inline("🎬 Putar Video", b"fmt_video")], [Button.inline("❌ Batal", b"fmt_cancel")]]
        return await event.respond("Pilih format pemutaran untuk link ini:", buttons=btns)
    
    if is_media_reply:
        try: title = reply_to_msg.file.name if reply_to_msg.file and getattr(reply_to_msg.file, 'name', None) else "Audio Telegram"
        except: title = "Audio Telegram"
        # Pesan status ini dikirim lewat `bot` (bukan `userbot`). Sebelumnya
        # pakai userbot.send_message, tapi sesi userbot belum tentu punya
        # entity chat ini ter-cache (kalau userbot belum pernah menerima
        # update apa pun dari chat tsb), sehingga Telethon gagal dengan
        # "Could not find the input entity" walau userbot sudah jadi
        # member grup. `bot` sudah pasti kenal chat ini karena event masuk
        # dari sana, dan msg_ub cuma teks status sementara (di-edit/hapus),
        # tidak perlu berasal dari akun userbot.
        msg_ub = await bot.send_message(chat_id, f"⏳ **Memproses media...**")
        task = asyncio.create_task(process_stream(chat_id, title, msg_ub, reply_to_msg, None, role, stream_type="audio", intent=intent))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        return

    loading_msg = await event.respond("🔍 *Mencari di YouTube...*")
    results = await search_youtube(query, limit=5)
    if not results: return await loading_msg.edit("❌ Tidak ditemukan.")
        
    cache_key = f"{chat_id}_{event.sender_id}"
    SEARCH_CACHE[cache_key] = {"query": query, "results": results, "page": 0, "role": role, "intent": intent}
    text = f"🔎 **Hasil:** `{query}`\n\n"
    for idx, res in enumerate(results): text += f"**{idx + 1}.** {res.get('title')[:40]}...\n"
    await loading_msg.edit(text, buttons=search_buttons(0, len(results)))

@bot.on(events.NewMessage(pattern=r'(?i)^/play(?:@\w+)?(?: |$)(.*)'))
async def play_cmd(event): await handle_play_or_queue(event, intent="play")

@bot.on(events.NewMessage(pattern=r'(?i)^/queue(?:@\w+)?(?: |$)(.*)'))
async def queue_cmd(event): await handle_play_or_queue(event, intent="queue")

@bot.on(events.CallbackQuery(pattern=b"delq_(.*)"))
async def queue_del_callback(event):
    action = event.data.decode().split('_')[1]
    chat_id = event.chat_id
    if action == "close": return await event.delete()
    if action == "all":
        await clear_queue(chat_id)
        return await event.edit("🗑 **Semua antrean berhasil dihapus.**")
        
    await remove_from_queue(int(action))
    q_list = await get_queue(chat_id)
    if not q_list: return await event.edit("Kosong! Tidak ada antrean musik saat ini.")
    
    text = "📜 **Daftar Antrean Musik:**\n\n"
    for i, data in enumerate(q_list): text += f"**{i+1}.** `{data[1]}`\n"
    await event.edit(text, buttons=queue_buttons(q_list))

@bot.on(events.CallbackQuery(pattern=b"fmt_(.*)"))
async def format_callback(event):
    data = event.data.decode().split('_')[1]
    cache_id = f"{event.chat_id}_{event.sender_id}"
    if cache_id not in FORMAT_CACHE: return await event.answer("Sesi habis.", alert=True)
    if data == "cancel":
        del FORMAT_CACHE[cache_id]
        return await event.delete()
        
    cache = FORMAT_CACHE.pop(cache_id)
    await event.delete()
    jenis = "AUDIO 🎵" if data == "audio" else "VIDEO 🎬"
    msg_ub = await bot.send_message(event.chat_id, f"⏳ **Memproses link sebagai {jenis}...**")
    task = asyncio.create_task(process_stream(event.chat_id, cache.get("title") or "Link Media", msg_ub, None, cache["query"], cache["role"], stream_type=data, intent=cache.get("intent", "play")))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

@bot.on(events.CallbackQuery(pattern=b"yt(sel|nav)_.*"))
async def yts_callback(event):
    cache_key = f"{event.chat_id}_{event.sender_id}"
    if cache_key not in SEARCH_CACHE: return await event.answer("Sesi habis.", alert=True)
    data = event.data.decode()
    cache = SEARCH_CACHE[cache_key]
    if "cancel" in data:
        del SEARCH_CACHE[cache_key]
        return await event.delete()
    if "ytsel" in data:
        idx = int(data.split("_")[1])
        selected = cache["results"][idx]
        FORMAT_CACHE[cache_key] = {
            "query": selected['url'], "role": cache['role'],
            "intent": cache.get("intent", "play"), "title": selected.get('title') or "Link Media",
        }
        btns = [[Button.inline("🎵 Audio", b"fmt_audio"), Button.inline("🎬 Video", b"fmt_video")],
                [Button.inline("❌ Batal", b"fmt_cancel")]]
        await event.edit(f"✅ <b>Dipilih:</b> {html.escape(selected.get('title') or '-')}\n\nPilih mode stream:",
                         buttons=btns, parse_mode="html")

@bot.on(events.NewMessage(pattern=r'(?i)^/(?:film|movie)(?:@\w+)?(?: |$)(.*)'))
async def film_cmd(event):
    if event.is_private: return await event.respond("❌ Perintah ini hanya untuk di grup.")
    is_allowed, role = await is_user_allowed(event, bot)
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    if not is_allowed: return 
    if role not in ['vip', 'admin'] and not is_owner: return await event.respond("❌ **AKSES DITOLAK: KHUSUS VIP**")
        
    query = event.pattern_match.group(1).strip()
    if not query: return await event.respond("⚠️ Gunakan: `/film [judul film]`")

    loading_msg = await event.respond("🎬 *Mencari film di database...* 🍿")
    results = await search_film_api(query)
    if not results: return await loading_msg.edit("❌ Film tidak ditemukan.")
        
    cache_key = f"{event.chat_id}_{event.sender_id}"
    FILM_CACHE[cache_key] = {"query": query, "results": results, "page": 0, "role": role}
    text = f"🎬 **Bioskop VIP:** `{query}`\n\n"
    for idx, res in enumerate(results): text += f"**{idx + 1}.** {res.get('title')[:45]}...\n"
    text += "\n*Pilih film yang ingin diputar di Voice Chat:*"
    await loading_msg.edit(text, buttons=film_buttons(0, len(results)))

@bot.on(events.CallbackQuery(pattern=b"flm(sel|nav)_.*"))
async def film_callback(event):
    cache_key = f"{event.chat_id}_{event.sender_id}"
    if cache_key not in FILM_CACHE: return await event.answer("Sesi habis.", alert=True)
    data = event.data.decode()
    cache = FILM_CACHE[cache_key]
    if "cancel" in data:
        del FILM_CACHE[cache_key]
        return await event.delete()
    if "flmsel" in data:
        idx = int(data.split("_")[1])
        selected = cache["results"][idx]
        await event.delete()
        msg_ub = await bot.send_message(event.chat_id, f"🎥 **BIOSKOP DIMULAI** 🍿\n⏳ Menyiapkan streaming...")
        target_url = selected["movie_id"] if selected.get("is_yt") else await get_film_stream_url(selected["movie_id"])
        if not target_url: return await msg_ub.edit("❌ Gagal menarik URL streaming.")
        task = asyncio.create_task(process_stream(event.chat_id, selected['title'], msg_ub, None, target_url, cache['role'], stream_type="video", intent="play"))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

async def process_stream(chat_id, title, msg_ub, reply_to_msg, target_url, role, stream_type="audio", intent="play"):
    check_active = await get_stream(chat_id)
    is_active = False
    
    if check_active and len(check_active) > 1:
        if check_active[1] in ["playing", "paused", "downloading"]: is_active = True

    if intent == "play":
        # Simpan path media lama sebelum ditimpa, supaya file yang sudah
        # tidak dipakai lagi (digantikan lagu baru) bisa langsung dihapus
        # dan tidak menumpuk percuma di folder downloads/.
        old_media = check_active[2] if check_active and len(check_active) > 2 else None
        await update_stream(chat_id, "stopped", "", 0, 0, 0)
        if old_media and old_media != target_url:
            await safe_delete(old_media)
        await asyncio.sleep(1) 
        is_active = False 

    try: 
        success, media_file, is_video = await download_and_play(chat_id, title, reply_to_msg, target_url, role, stream_type, play_now=not is_active)
    except TypeError: 
        success, media_file, is_video = await download_and_play(chat_id, title, reply_to_msg, target_url, role)
        
    if success:
        if is_active and intent == "queue":
            from config import ADMIN_ID
            if role == 'user' and str(msg_ub.chat_id) != str(ADMIN_ID): 
                current_q = await get_queue(chat_id)
                if len(current_q) >= 5:
                    return await msg_ub.edit("❌ **Limit Antrean Tercapai!**\nUser Biasa maksimal hanya dapat memasukkan 5 lagu.\n🔥 *Upgrade VIP untuk antrean tanpa batas!*")

            await add_to_queue(chat_id, title, role, media_file, is_video)
            return await msg_ub.edit(f"📝 **Antrean Ditambahkan:**\n`{title}`\n\n_Ketik /queue untuk melihat daftar._")

        await msg_ub.delete()
        duration_raw = await get_duration_smart(media_file)
        int_duration = parse_time(duration_raw)
        
        await update_stream(chat_id, "playing", media_file, 0, int_duration, 0)
        await set_stream_role(chat_id, role) 
        
        panel_msg = await send_stream_panel(chat_id, title, media_file, is_video, role, int_duration, duration_raw)
            
        task = asyncio.create_task(progress_bar_updater(chat_id, panel_msg, int_duration, role))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        
    else:
        if not is_active: await update_stream(chat_id, "stopped", "", 0, 0, 0)
        reason = media_file if isinstance(media_file, str) and media_file.startswith("ERROR") else "Sistem gagal memproses link tersebut (atau batas VIP terlampaui)."
        await msg_ub.edit(f"❌ **Gagal Memutar Media!**\n`{reason[:300]}`")

async def progress_bar_updater(chat_id, message, total_duration, role):
    # Diperlambat dari 1 detik ke 5 detik: progress bar musik tidak perlu
    # presisi per detik, sementara versi lama membebani DB + Telegram API
    # (edit_message) setiap detik untuk SETIAP grup yang sedang streaming.
    # Ini mengurangi jumlah query & panggilan API sampai 5x lipat.
    update_interval = 5
    total_duration = parse_time(total_duration)
    
    while True:
        await asyncio.sleep(update_interval)
        stream_data = await get_stream(chat_id)
        
        if not stream_data or stream_data[1] == "stopped": 
            try: await message.delete() 
            except: pass
            break 
            
        status, media, is_loop, duration, current_time = stream_data[1:]
        
        if status == "playing":
            try:
                c_time = parse_time(current_time)
                new_time = c_time + update_interval
                if new_time >= total_duration:
                    if is_loop == 1: new_time = 0
                    else: new_time = total_duration
                await update_time(chat_id, new_time)
                await message.edit(buttons=stream_controls(new_time, total_duration, bool(is_loop), role, is_paused=False))
            except Exception as e:
                if "message" not in str(e).lower(): pass
