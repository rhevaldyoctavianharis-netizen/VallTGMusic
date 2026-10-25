import os
import asyncio
import yt_dlp
from pytgcalls.types import MediaStream
from core.call import call
from database.db import update_stream

def sync_search_youtube(query, limit=5, start=0):
    ydl_opts = {'extract_flat': True, 'quiet': True}
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{start+limit}:{query}", download=False)
            return info.get('entries', [])[start:start+limit]
    except Exception as e:
        print(f"YTS Error: {e}")
        return []

async def search_youtube(query, limit=5, start=0):
    return await asyncio.to_thread(sync_search_youtube, query, limit, start)

def sync_download(url, role, stream_type="audio"):
    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s', 
        'quiet': True, 
        'noplaylist': True
    }
    
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'

    
    if stream_type == "audio":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            dur = info.get('duration', 0)
            size = info.get('filesize') or info.get('filesize_approx') or 0
            
            if role == 'user':
                if dur > 60: return f"ERROR: Durasi video ({dur} detik) melebihi batas User (Maks 60s)."
                if size > 104857600: return "ERROR: Ukuran file melebihi batas User (Maks 100MB)."
                    
            info = ydl.extract_info(url, download=True)
            
            if stream_type == "audio":
                file_path = f"downloads/{info['id']}.mp3"
                if os.path.exists(file_path):
                    return file_path
            return f"downloads/{info['id']}.{info['ext']}"
        except Exception as e:
            return f"ERROR: {str(e)}"

async def download_and_play(chat_id: int, query: str, reply_to_msg=None, url=None, role='user', stream_type="audio", play_now=True):
    if play_now:
        await update_stream(chat_id, "downloading", query, 0, 0, 0)
        
    media_file = ""
    is_video = False
    
    try:
        if reply_to_msg and (reply_to_msg.audio or reply_to_msg.video or reply_to_msg.voice):
            if role == 'user' and reply_to_msg.file:
                if reply_to_msg.file.size > 104857600: 
                    return False, "ERROR: Ukuran file melebihi batas 100MB.", False
                if hasattr(reply_to_msg.document.attributes[0], 'duration') and reply_to_msg.document.attributes[0].duration > 60:
                     return False, "ERROR: Durasi melebihi 60 detik.", False

            if reply_to_msg.video: is_video = True
            if not os.path.exists("downloads"): os.makedirs("downloads")
            media_file = await reply_to_msg.download_media(file="downloads/")
            
        elif url:
            if not os.path.exists("downloads"): os.makedirs("downloads")
            media_file = await asyncio.to_thread(sync_download, url, role, stream_type)
            if media_file.startswith("ERROR:"): return False, media_file, False
            if stream_type == "video" or media_file.endswith(('.mp4', '.webm', '.mkv', '.flv')): 
                is_video = True
        else:
            return False, None, False

        if not media_file or not os.path.exists(media_file): return False, None, False

        if play_now:
            await call.play(chat_id, MediaStream(media_file))
            await update_stream(chat_id, "playing", media_file, 0, 0, 0)
        
        return True, media_file, is_video
    except Exception as e:
        print(f"Stream Error: {e}")
        return False, None, False
