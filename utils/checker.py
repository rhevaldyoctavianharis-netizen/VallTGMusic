from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon import Button
import config
from database.db import get_user_full, update_user, is_group_banned
from utils.inline import _safe_url_button
import time

# Cache singkat status keanggotaan FSUB channel per user. Sebelumnya
# is_user_allowed() memanggil GetParticipantRequest ke Telegram API pada
# SETIAP perintah (play, queue, dll) -- padahal status join channel
# jarang berubah. Dengan cache 10 menit, panggilan API turun drastis
# tanpa mengorbankan akurasi secara berarti.
_FSUB_CACHE_TTL = 600
_fsub_cache = {}

async def is_user_allowed(event, bot):
    user_id = event.sender_id
    chat_id = event.chat_id
    
    if chat_id:
        banned = await is_group_banned(chat_id)
        if banned: return False, "user"
            
    u_data = await get_user_full(user_id)
    if not u_data:
        try:
            me = await bot.get_me()
            btn = _safe_url_button("🤖 Mulai Bot", f"https://t.me/{me.username}?start=true" if me.username else "")
            await event.respond(
                "⚠️ **Anda belum terdaftar di database!**\nSilakan mulai bot ini di Private Chat terlebih dahulu.",
                buttons=[[btn]] if btn else None,
            )
        except: pass
        return False, "user"
        
    role, status, points, vip_until = u_data[:4]
    
    if role == 'vip' and vip_until > 0 and time.time() > vip_until:
        await update_user(user_id, "role", "user")
        await update_user(user_id, "vip_until", 0)
        role = "user"
        try: await event.respond("⚠️ **Masa aktif VIP Anda telah habis!**\nAnda kembali menjadi User Biasa.")
        except: pass
    
    if status == 'banned':
        try: await event.answer("❌ Anda di-banned!", alert=True) 
        except: await event.respond("❌ Anda di-banned dari bot ini.")
        return False, role
        
    if config.FSUB_CHANNEL:
        cached_until = _fsub_cache.get(user_id, 0)
        if cached_until < time.time():
            try:
                await bot(GetParticipantRequest(config.FSUB_CHANNEL, user_id))
                _fsub_cache[user_id] = time.time() + _FSUB_CACHE_TTL
            except UserNotParticipantError:
                _fsub_cache.pop(user_id, None)
                join_btn = _safe_url_button(
                    "📢 Join Channel", f"https://t.me/{config.FSUB_CHANNEL.replace('@', '')}"
                )
                btn = [[join_btn]] if join_btn else None
                try:
                    await event.answer("⚠️ Anda harus join channel!", alert=True)
                    await event.respond("⚠️ Anda wajib join channel kami untuk memutar lagu!", buttons=btn)
                except:
                    await event.respond("⚠️ Anda wajib join channel kami untuk memutar lagu!", buttons=btn)
                return False, role
            except Exception:
                pass

    return True, role
