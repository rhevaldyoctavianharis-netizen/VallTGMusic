import os
import html
from core.bot import bot
from utils.inline import stream_controls
from utils.streamer import get_meta, fetch_thumbnail
from utils.media import get_duration, get_thumbnail

_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def _num(n):
    return f"{int(n):,}".replace(",", ".")


def _dur(sec):
    sec = int(sec or 0)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _date(ymd):
    try:
        return f"{int(ymd[6:8])} {_BULAN[int(ymd[4:6]) - 1]} {ymd[:4]}"
    except Exception:
        return None


def build_caption(title, meta, is_video):
    """Caption HTML lengkap (tanpa deskripsi). Fallback sederhana bila tak ada metadata."""
    icon = "🎬" if is_video else "🎵"
    mode = "Video" if is_video else "Audio"
    if not meta:
        return f"{icon} <b>Sedang Memutar ({mode}):</b> <code>{html.escape(str(title))}</code>"

    url = meta.get("url")
    t = html.escape((meta.get("title") or str(title))[:120])
    title_line = f'<a href="{html.escape(url, quote=True)}">{t}</a>' if url else t

    lines = [f"{icon} <b>Sedang Memutar ({mode})</b>", f"<b>{title_line}</b>", ""]

    ch = meta.get("channel")
    if ch:
        chn = html.escape(ch)
        cu = meta.get("channel_url")
        chn = f'<a href="{html.escape(cu, quote=True)}">{chn}</a>' if cu else chn
        subs = meta.get("subscribers")
        lines.append(f"📺 <b>Channel:</b> {chn}" + (f" ({_num(subs)} subscriber)" if subs else ""))
    if meta.get("view_count") is not None:
        lines.append(f"👁 <b>Views:</b> {_num(meta['view_count'])}")
    lines.append("👍 <b>Like:</b> " + (_num(meta["like_count"]) if meta.get("like_count") is not None else "disembunyikan"))
    if meta.get("comment_count") is not None:
        lines.append(f"💬 <b>Komentar:</b> {_num(meta['comment_count'])}")
    if meta.get("duration"):
        lines.append(f"⏱ <b>Durasi:</b> {_dur(meta['duration'])}")
    d = _date(meta.get("upload_date") or "")
    if d:
        lines.append(f"📅 <b>Upload:</b> {d}")
    if url:
        lines.append(f"🔗 <b>Link:</b> {html.escape(url)}")
    return "\n".join(lines)[:1000]


async def get_duration_smart(media_file):
    """ffprobe dulu; kalau gagal/0 pakai durasi dari metadata yt-dlp."""
    d = await get_duration(media_file)
    if not d:
        meta = get_meta(media_file)
        d = (meta or {}).get("duration") or 0
    return d


async def send_stream_panel(chat_id, title, media_file, is_video, role, int_duration, duration_raw=0):
    """Kirim panel controller: thumbnail + caption lengkap + tombol kontrol."""
    meta = get_meta(media_file)
    caption = build_caption(title, meta, is_video)
    buttons = stream_controls(0, int_duration, False, role)

    thumb = None
    try:
        if meta:
            thumb = await fetch_thumbnail(meta, chat_id)
        if not thumb and is_video:
            thumb = await get_thumbnail(media_file, duration_raw)
    except Exception as e:
        print(f"[panel] thumbnail gagal: {e}")

    try:
        if thumb and os.path.exists(thumb):
            return await bot.send_file(chat_id, file=thumb, caption=caption, buttons=buttons, parse_mode="html")
        return await bot.send_message(chat_id, caption, buttons=buttons, parse_mode="html", link_preview=False)
    except Exception as e:
        print(f"[panel] kirim panel gagal ({type(e).__name__}: {e}), pakai fallback polos")
        return await bot.send_message(chat_id, f"Sedang Memutar: {title}", buttons=buttons, parse_mode=None)
    finally:
        if thumb:
            try: os.remove(thumb)
            except Exception: pass
