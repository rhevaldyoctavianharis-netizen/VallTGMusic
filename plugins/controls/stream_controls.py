from telethon import events
from core.bot import bot
from core.call import call
from database.db import get_stream, update_stream, toggle_loop, clear_queue, get_all_active_streams, get_queue, pop_queue, ban_group, unban_group, get_all_banned_groups
from utils.inline import stream_controls, listplay_buttons, listban_buttons, ban_msg_btn
from utils.checker import is_user_allowed
from utils.media import safe_delete
import os
import config
import asyncio
from pytgcalls.types import MediaStream

@bot.on(events.CallbackQuery(pattern=b"ctrl_"))
async def stream_controller(event):
    is_allowed, role = await is_user_allowed(event, bot)
    if not is_allowed: return

    chat_id = event.chat_id
    action = event.data.decode().split('_')[1]
    if action == "ignore": return await event.answer()
        
    stream_data = await get_stream(chat_id)
    if not stream_data: return await event.answer("Tidak ada stream aktif.", alert=True)

    status, current_media, is_loop, duration, current_time = stream_data[1:]

    try:
        if action == "pause":
            await call.pause(chat_id)
            await update_stream(chat_id, "paused", current_media, is_loop, duration, current_time)
            await event.edit(buttons=stream_controls(current_time, duration, bool(is_loop), role, is_paused=True))
            await event.answer("Stream di-pause.")
            
        elif action == "resume":
            await call.resume(chat_id)
            await update_stream(chat_id, "playing", current_media, is_loop, duration, current_time)
            await event.edit(buttons=stream_controls(current_time, duration, bool(is_loop), role, is_paused=False))
            await event.answer("Stream dilanjutkan.")
            
        elif action == "stop":
            # Hapus semua file di antrean sekaligus file yang sedang diputar,
            # karena setelah /stop tidak ada yang akan memakainya lagi.
            q_list = await get_queue(chat_id)
            await update_stream(chat_id, "stopped", "", 0, 0, 0)
            await clear_queue(chat_id)
            try: await event.message.delete()
            except: pass
            try: await call.leave_call(chat_id)
            except: pass
            await safe_delete(current_media)
            for item in q_list:
                await safe_delete(item[3])
            
        elif action == "loop":
            if role not in ['vip', 'admin'] and str(event.sender_id) != str(config.ADMIN_ID):
                return await event.answer("❌ Fitur Loop eksklusif untuk VIP/Admin!", alert=True)
            new_loop = await toggle_loop(chat_id)
            await event.answer("Loop dimatikan." if new_loop == 0 else "Loop dihidupkan.")
            await event.edit(buttons=stream_controls(current_time, duration, is_loop=(new_loop == 1), role=role, is_paused=(status=="paused")))
            
        elif action == "skip_q":
            q_list = await get_queue(chat_id)
            if not q_list: return await event.answer("❌ Tidak ada lagu di antrean!", alert=True)

            await event.answer("⏭ Memuat antrean selanjutnya...")
            await update_stream(chat_id, "stopped", "", 0, 0, 0)
            try: await call.leave_call(chat_id)
            except: pass
            try: await event.message.delete()
            except: pass

            await safe_delete(current_media)
            await asyncio.sleep(1) 
            next_data = await pop_queue(chat_id)
            if next_data:
                q_id, title, role_q, media_file, is_video = next_data
                if not os.path.exists(media_file): return await bot.send_message(chat_id, "❌ File media terhapus.")
                try: await call.play(chat_id, MediaStream(media_file))
                except Exception as e: return await bot.send_message(chat_id, f"❌ Error PyTgCalls: {e}")

                from utils.panel import send_stream_panel, get_duration_smart
                from plugins.bot.play import parse_time, progress_bar_updater, background_tasks

                duration_raw = await get_duration_smart(media_file)
                int_duration = parse_time(duration_raw)
                await update_stream(chat_id, "playing", media_file, 0, int_duration, 0)
                panel_msg = await send_stream_panel(chat_id, title, media_file, bool(is_video), role_q, int_duration, duration_raw)

                task = asyncio.create_task(progress_bar_updater(chat_id, panel_msg, int_duration, role_q))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
            
        elif action == "next":
            new_time = current_time + 5
            if new_time >= duration: return await event.answer("Gunakan tombol 'Next Music'!", alert=True)
            await event.answer("⏩ Melompati +5 detik...")
            skip_file = f"downloads/skip_{chat_id}.mkv"
            # Sebelumnya memakai os.system() yang MENGEKSEKUSI ffmpeg secara
            # blocking -- ini membekukan seluruh bot (semua grup lain ikut
            # macet) selama proses potong video berjalan. Diganti dengan
            # subprocess async agar hanya menunggu tanpa memblokir event loop.
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-ss", str(new_time), "-i", current_media,
                "-c", "copy", skip_file, "-loglevel", "error",
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate()
            if os.path.exists(skip_file):
                await call.play(chat_id, MediaStream(skip_file))
                # File asli (sebelum dipotong) sudah tidak dipakai lagi setelah
                # digantikan potongan baru -- hapus supaya tidak jadi sampah,
                # kecuali kalau file lama itu sendiri adalah skip_file (menimpa diri sendiri).
                if current_media != skip_file:
                    await safe_delete(current_media)
                await update_stream(chat_id, "playing", skip_file, is_loop, duration, new_time)
                await event.edit(buttons=stream_controls(new_time, duration, bool(is_loop), role=role, is_paused=False))
            else:
                await event.answer("❌ Gagal memotong media!", alert=True)

    except Exception as e:
        await event.answer(f"Error: {str(e)}", alert=True)

@bot.on(events.CallbackQuery(pattern=b"fstop_(.*)"))
async def force_stop_callback(event):
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    if not is_owner: return await event.answer("Akses Ditolak!", alert=True)
        
    chat_id_target = int(event.data.decode().split('_')[1])
    old_stream = await get_stream(chat_id_target)
    old_queue = await get_queue(chat_id_target)
    try: await call.leave_call(chat_id_target)
    except: pass
    
    await update_stream(chat_id_target, "stopped", "", 0, 0, 0)
    await clear_queue(chat_id_target)
    if old_stream and len(old_stream) > 2: await safe_delete(old_stream[2])
    for item in old_queue: await safe_delete(item[3])
    await event.answer(f"Stream di grup {chat_id_target} dihentikan paksa!", alert=True)
    
    streams, total = await get_all_active_streams(5, 0)
    if not streams: return await event.edit("ℹ️ Server kosong. Tidak ada grup yang sedang memutar stream.")
    
    total_pages = (total // 5) + (1 if total % 5 != 0 else 0)
    text = f"📊 **DASHBOARD SERVER ({total} Grup Aktif):**\n\n"
    for s in streams: text += f"🔹 **Group ID:** `{s[0]}`\n🎵 **Status:** `{s[2].upper()}`\n\n"
    await event.edit(text, buttons=listplay_buttons(streams, 0, total_pages))

@bot.on(events.CallbackQuery(pattern=b"fban_(.*)"))
async def force_ban_callback(event):
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    if not is_owner: return await event.answer("Akses Ditolak!", alert=True)
        
    chat_id_target = int(event.data.decode().split('_')[1])
    old_stream = await get_stream(chat_id_target)
    old_queue = await get_queue(chat_id_target)
    try: await call.leave_call(chat_id_target)
    except: pass
    
    await update_stream(chat_id_target, "stopped", "", 0, 0, 0)
    await clear_queue(chat_id_target)
    await ban_group(chat_id_target)
    if old_stream and len(old_stream) > 2: await safe_delete(old_stream[2])
    for item in old_queue: await safe_delete(item[3])
    
    try:
        msg = "⚠️ **Kami mendeteksi adanya tindakan ilegal dalam menggunakan bot ini.**\n\nGrup ini diblokir untuk sementara. Hubungi admin untuk bantuan."
        await bot.send_message(chat_id_target, msg, buttons=ban_msg_btn(config.ADMIN_ID))
    except Exception as e: print(f"Gagal mengirim pesan banned: {e}")
        
    await event.answer(f"Grup {chat_id_target} dihentikan dan di-BANNED!", alert=True)
    
    streams, total = await get_all_active_streams(5, 0)
    if not streams: return await event.edit("ℹ️ Server kosong.")
    total_pages = (total // 5) + (1 if total % 5 != 0 else 0)
    text = f"📊 **DASHBOARD SERVER ({total} Grup Aktif):**\n\n"
    for s in streams: text += f"🔹 **Group ID:** `{s[0]}`\n🎵 **Status:** `{s[2].upper()}`\n\n"
    await event.edit(text, buttons=listplay_buttons(streams, 0, total_pages))

@bot.on(events.CallbackQuery(pattern=b"unban_(.*)"))
async def unban_callback(event):
    is_owner = (str(event.sender_id) == str(config.ADMIN_ID))
    if not is_owner: return await event.answer("Akses Ditolak!", alert=True)
        
    chat_id_target = int(event.data.decode().split('_')[1])
    await unban_group(chat_id_target)
    await event.answer(f"Grup {chat_id_target} berhasil di-unbanned!", alert=True)
    
    banned = await get_all_banned_groups()
    if not banned: return await event.edit("✅ Server bersih. Tidak ada grup yang di-banned.")
    
    total = len(banned)
    total_pages = (total // 5) + (1 if total % 5 != 0 else 0)
    current_banned = banned[0:5]
    
    text = f"🚫 **DAFTAR GRUP BANNED ({total} Grup):**\n\n"
    for b in current_banned: text += f"🔹 **Group ID:** `{b[0]}`\n"
    await event.edit(text, buttons=listban_buttons(current_banned, 0, total_pages))

@bot.on(events.CallbackQuery(pattern=b"lpnav_(.*)"))
async def listplay_nav(event):
    action = event.data.decode().split('_')[1]
    if action == "close": return await event.delete()
    
    page = int(action)
    streams, total = await get_all_active_streams(5, page * 5)
    total_pages = (total // 5) + (1 if total % 5 != 0 else 0)
    
    text = f"📊 **DASHBOARD SERVER ({total} Grup Aktif):**\n\n"
    for s in streams: text += f"🔹 **Group ID:** `{s[0]}`\n🎵 **Status:** `{s[2].upper()}`\n\n"
    await event.edit(text, buttons=listplay_buttons(streams, page, total_pages))

@bot.on(events.CallbackQuery(pattern=b"lbnav_(.*)"))
async def listban_nav(event):
    action = event.data.decode().split('_')[1]
    if action == "close": return await event.delete()
    
    page = int(action)
    banned = await get_all_banned_groups()
    total = len(banned)
    total_pages = (total // 5) + (1 if total % 5 != 0 else 0)
    current_banned = banned[page * 5:(page + 1) * 5]
    
    text = f"🚫 **DAFTAR GRUP BANNED ({total} Grup):**\n\n"
    for b in current_banned: text += f"🔹 **Group ID:** `{b[0]}`\n"
    await event.edit(text, buttons=listban_buttons(current_banned, page, total_pages))
