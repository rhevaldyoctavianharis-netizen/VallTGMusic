import os
import asyncio
import yt_dlp
import aiohttp
from pytgcalls.types import MediaStream
from core.call import call
from database.db import update_stream


# ---------------------------------------------------------------------------
# Metadata media (judul, channel, like, views, dst.) -- disimpan di memori,
# kunci = path file hasil download. Dipakai untuk caption controller stream.
# ---------------------------------------------------------------------------
MEDIA_META = {}

def _extract_meta(info: dict) -> dict:
    vid = info.get('id')
    return {
        'id': vid,
        'title': info.get('title'),
        'channel': info.get('channel') or info.get('uploader'),
        'channel_url': info.get('channel_url') or info.get('uploader_url'),
        'subscribers': info.get('channel_follower_count'),
        'view_count': info.get('view_count'),
        'like_count': info.get('like_count'),
        'comment_count': info.get('comment_count'),
        'duration': info.get('duration'),
        'upload_date': info.get('upload_date'),          # YYYYMMDD
        'url': info.get('webpage_url') or (f"https://www.youtube.com/watch?v={vid}" if vid else None),
        'thumbnail': info.get('thumbnail'),
        'extractor_key': info.get('extractor_key') or '',
    }

def _store_meta(path: str, info: dict):
    try:
        MEDIA_META[path] = _extract_meta(info)
        while len(MEDIA_META) > 200:              # batasi pemakaian RAM
            MEDIA_META.pop(next(iter(MEDIA_META)))
    except Exception as e:
        print(f"[meta] gagal simpan metadata: {e}")

def get_meta(path: str):
    return MEDIA_META.get(path)

async def fetch_thumbnail(meta: dict, chat_id: int):
    """Unduh thumbnail (jpg) ke downloads/. Return path file atau None."""
    vid = meta.get('id')
    cands = []
    if str(meta.get('extractor_key', '')).lower().startswith('youtube') and vid:
        cands += [f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
                  f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"]
    t = meta.get('thumbnail')
    if t and t.lower().split('?')[0].endswith(('.jpg', '.jpeg', '.png')):
        cands.append(t)
    if not cands:
        return None
    os.makedirs("downloads", exist_ok=True)
    out = f"downloads/thumb_{chat_id}_{vid or 'x'}.jpg"
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as sess:
        for u in cands:
            try:
                async with sess.get(u) as r:
                    if r.status == 200 and (r.content_type or '').startswith('image/'):
                        data = await r.read()
                        if len(data) > 2000:
                            await asyncio.to_thread(lambda: open(out, 'wb').write(data))
                            return out
            except Exception:
                continue
    return None


def _yt_base_opts():
    """Opsi dasar yt-dlp: JS runtime (wajib utk solve signature/n-challenge) + cookies."""
    opts = {
        'quiet': True,
        'noplaylist': True,
        # Butuh runtime JS. Pasang `deno` lewat requirements.txt (lihat catatan).
        'js_runtimes': {'deno': {}, 'node': {}},
        # Fallback: unduh solver EJS dari GitHub jika paket yt-dlp-ejs tidak ada.
        'remote_components': ['ejs:github'],
    }
    if os.path.exists("cookies.txt"):
        opts['cookiefile'] = 'cookies.txt'
    return opts

def sync_search_youtube(query, limit=5, start=0):
    ydl_opts = _yt_base_opts()
    ydl_opts['extract_flat'] = True
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{start+limit}:{query}", download=False)
            return info.get('entries', [])[start:start+limit]
    except Exception as e:
        print(f"YTS Error: {e}")
        return []

async def search_youtube(query, limit=5, start=0):
    return await asyncio.to_thread(sync_search_youtube, query, limit, start)

# Urutan percobaan client YouTube. None = default yt-dlp (paling stabil).
# Percobaan berikutnya hanya dipakai bila yang sebelumnya gagal dgn error format/bot.
_CLIENT_ATTEMPTS = [None, "player_client=web_safari,mweb", "player_client=tv,web"]
_RETRY_HINTS = ("format is not available", "sign in", "signature", "challenge", "403", "only images")


def _clean_err(e) -> str:
    import re
    msg = re.sub(r"\x1b\[[0-9;]*m", "", str(e))   # buang kode warna ANSI
    return msg.replace("`", "'").strip()


def sync_download(url, role, stream_type="audio"):
    last_err = "Unknown"
    for attempt in _CLIENT_ATTEMPTS:
        ydl_opts = _yt_base_opts()
        ydl_opts['outtmpl'] = 'downloads/%(id)s.%(ext)s'
        if attempt:
            ydl_opts['extractor_args'] = {'youtube': [attempt]}

        if stream_type == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = ('bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/'
                                   'best[height<=720][ext=mp4]/best[height<=720]/best')

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Cek batas role hanya utk user biasa (butuh 1x ekstraksi tambahan).
                # VIP/admin langsung unduh -> hemat 1x proses solve JS (lambat).
                if role == 'user':
                    pre = ydl.extract_info(url, download=False)
                    dur = pre.get('duration') or 0
                    size = pre.get('filesize') or pre.get('filesize_approx') or 0
                    if dur > 60: return f"ERROR: Durasi video ({dur} detik) melebihi batas User (Maks 60s)."
                    if size > 104857600: return "ERROR: Ukuran file melebihi batas User (Maks 100MB)."

                info = ydl.extract_info(url, download=True)

                if stream_type == "audio":
                    file_path = f"downloads/{info['id']}.mp3"
                    if os.path.exists(file_path):
                        _store_meta(file_path, info)
                        return file_path
                file_path = f"downloads/{info['id']}.{info['ext']}"
                _store_meta(file_path, info)
                return file_path
        except Exception as e:
            last_err = _clean_err(e)
            print(f"[yt-dlp] percobaan client={attempt or 'default'} gagal: {last_err[:300]}")
            if not any(h in last_err.lower() for h in _RETRY_HINTS):
                break   # error lain (mis. ffmpeg hilang) -> retry tidak membantu
    return f"ERROR: {last_err[:350]}"

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
            try:
                await call.play(chat_id, MediaStream(media_file))
            except Exception as e:
                import traceback; traceback.print_exc()
                return False, f"ERROR: Gagal stream ke Voice Chat -> {type(e).__name__}: {_clean_err(e)[:250]}", False
            await update_stream(chat_id, "playing", media_file, 0, 0, 0)
        
        return True, media_file, is_video
    except Exception as e:
        import traceback; traceback.print_exc()
        return False, f"ERROR: {type(e).__name__}: {_clean_err(e)[:250]}", False
