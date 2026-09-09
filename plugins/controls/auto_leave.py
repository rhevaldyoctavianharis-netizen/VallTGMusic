from core.call import call
from database.db import get_stream, update_stream, pop_queue, clear_queue, set_stream_role, get_queue
from pytgcalls.types import Update, MediaStream
from pytgcalls.types.stream import StreamEnded 
from utils.media import safe_delete
import os
import asyncio

async def play_next_queue(chat_id):
    from plugins.bot.play import progress_bar_updater, background_tasks, parse_time
    from core.bot import bot
    from utils.media import get_duration, get_thumbnail
    from utils.inline import stream_controls
    
    next_data = await pop_queue(chat_id)
    
    if next_data:
        q_id, title, role_q, media_file, is_video = next_data
        if not os.path.exists(media_file): return await play_next_queue(chat_id)
            
        try: await call.play(chat_id, MediaStream(media_file))
        except Exception as e:
            print(f"Error putar antrean: {e}")
            return await play_next_queue(chat_id)
            
        duration_raw = await get_duration(media_file)
        int_duration = parse_time(duration_raw)
        
        await update_stream(chat_id, "playing", media_file, 0, int_duration, 0)
        await set_stream_role(chat_id, role_q)
        
        thumb_path = await get_thumbnail(media_file, duration_raw) if bool(is_video) else None
        caption = f"🎵 **Sedang Memutar:** `{title}`"
        
        if thumb_path and os.path.exists(thumb_path):
            panel_msg = await bot.send_file(chat_id, file=thumb_path, caption=caption, buttons=stream_controls(0, int_duration, False, role_q))
            os.remove(thumb_path)
        else:
            panel_msg = await bot.send_message(chat_id, caption, buttons=stream_controls(0, int_duration, False, role_q))
            
        task = asyncio.create_task(progress_bar_updater(chat_id, panel_msg, int_duration, role_q))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        return True
        
    return False

@call.on_update()
async def stream_ended_handler(client, update: Update):
    chat_id = update.chat_id
    update_name = type(update).__name__
    
    if update_name in ['LeftGroupCall', 'ClosedGroupCall', 'Kicked']:
        old_stream = await get_stream(chat_id)
        old_queue = await get_queue(chat_id)
        await update_stream(chat_id, "stopped", "", 0, 0, 0)
        await clear_queue(chat_id)
        if old_stream and len(old_stream) > 2: await safe_delete(old_stream[2])
        for item in old_queue: await safe_delete(item[3])
        print(f"⏹ Bot keluar dari {chat_id} (Ditendang/VC Ditutup).")
        return

    if isinstance(update, StreamEnded) or update_name == "StreamEnded":
        stream_data = await get_stream(chat_id)
        if stream_data:
            status, current_media, is_loop, duration, current_time = stream_data[1:]
            
            if is_loop == 1 and current_media:
                try:
                    await client.play(chat_id, MediaStream(current_media))
                    await update_stream(chat_id, "playing", current_media, 1, duration, 0)
                    return 
                except Exception: pass

            # Lagu benar-benar selesai (tidak loop) -- filenya sudah tidak
            # dipakai lagi, bersihkan sebelum lanjut ke antrean berikutnya.
            if current_media: await safe_delete(current_media)

        has_next = await play_next_queue(chat_id)
        if has_next: return 
            
        try: await client.leave_call(chat_id)
        except: pass
        await update_stream(chat_id, "stopped", "", 0, 0, 0)
