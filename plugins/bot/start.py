from telethon import events, Button
from core.bot import bot
from utils.inline import start_buttons, _safe_url_button
from utils.image_gen import generate_start_image
from utils.checker import is_user_allowed
from database.db import add_or_get_user, get_user_full, update_user, try_purchase_vip
from urllib.parse import urlencode
import os
import asyncio

@bot.on(events.NewMessage(pattern=r'^/start(?: |$)(.*)'))
async def start_cmd(event):
    if event.is_private:
        user = await event.get_sender()
        user_id = event.sender_id
        
        # SISTEM REFERRAL (Menangkap ID Pengundang dari link t.me/bot?start=ref_123)
        args = event.pattern_match.group(1).strip()
        referrer_id = None
        if args.startswith("ref_"):
            try: referrer_id = int(args.split("_")[1])
            except: pass
            
        # Catat User (Jika baru, pengundang dapat +1 poin di dalam db.py)
        role, status, is_new = await add_or_get_user(user_id, getattr(user, 'first_name', 'User'), referrer_id)
        
        # Notifikasi untuk pengundang
        if is_new and referrer_id and referrer_id != user_id:
            try:
                await bot.send_message(referrer_id, f"🎉 **HORE!** Seseorang telah menggunakan link Anda.\nAnda mendapatkan **+1 Poin!** Cek `/start` lalu buka Shop.")
            except: pass

        # Cek izin standar
        is_allowed, role = await is_user_allowed(event, bot)
        if not is_allowed: return
            
        me = await bot.get_me()
        loading_msg = await event.respond("⏳ *Menyiapkan Data Anda...*")
        pfp_path = "default_pfp.jpg"
        if user.photo:
            pfp_path = await bot.download_profile_photo(user_id, file=f"pfp_{user_id}.jpg")
            
        out_image = f"start_{user_id}.jpg"
        # generate_start_image() memakai PIL secara sinkron (buka file, resize,
        # render font, encode JPEG) -- kalau dipanggil langsung, ini memblokir
        # SELURUH bot (semua grup & user lain) selama proses render gambar.
        # Dijalankan di thread terpisah agar event loop tetap responsif.
        await asyncio.to_thread(generate_start_image, pfp_path, getattr(user, 'first_name', 'User'), out_image)
        
        is_prem = role in ['vip', 'admin']
        c, s = "✅", "❌"
        
        caption = (
            f"**Halo {getattr(user, 'first_name', 'User')}!** 👋\n\n"
            f"**[ INFORMASI AKUN ]**\n"
            f"👤 **Status Role:** `{role.upper()}`\n\n"
            f"**[ FITUR AKSES ]**\n"
            f"🎵 Play Musik & Video : {c}\n"
            f"🔍 Pencarian YouTube : {c}\n"
            f"⏱ Durasi Tanpa Batas : {c if is_prem else s}\n"
            f"💾 File Media >100MB : {c if is_prem else s}\n"
            f"🔁 Loop Auto-Play : {c if is_prem else s}\n\n"
            f"Gunakan tombol di bawah untuk navigasi."
        )
        
        await bot.send_file(event.chat_id, file=out_image, caption=caption, buttons=start_buttons(me.username))
        
        await loading_msg.delete()
        if pfp_path and os.path.exists(pfp_path) and "default" not in pfp_path: os.remove(pfp_path)
        if os.path.exists(out_image): os.remove(out_image)

@bot.on(events.CallbackQuery(pattern=b"menu_.*"))
async def callback_dispatcher(event):
    is_allowed, role = await is_user_allowed(event, bot)
    if not is_allowed: return
    data = event.data

    if data == b"menu_help":
        text_help = (
            "**📖 CARA PENGGUNAAN BOT**\n\n"
            "1️⃣ Tambahkan bot ini ke Grup Telegram Anda.\n"
            "2️⃣ Jadikan bot sebagai **Admin** di grup tersebut.\n"
            "3️⃣ Mulai Obrolan Suara (Voice Chat) di grup.\n\n"
            "**Daftar Perintah (Gunakan di Grup):**\n"
            "🎵 `/play [judul lagu]` - Memutar dari YouTube.\n"
            "🔗 `/play [link YT/IG/Tiktok]` - Memutar dari link luar.\n"
            "📁 *Balas (reply) file lagu/video dengan perintah `/play`*\n\n"
            "💡 *User biasa memiliki batas durasi 60 detik. Kumpulkan poin di Shop untuk menjadi VIP.*"
        )
        await event.edit(text_help, buttons=[Button.inline("🔙 Kembali", b"menu_back")])
        
    # MENU SHOP & AFFILIATE
    elif data == b"menu_shop":
        user_data = await get_user_full(event.sender_id)
        points = user_data[2]
        me = await bot.get_me()
        ref_link = f"https://t.me/{me.username}?start=ref_{event.sender_id}"
        
        text_shop = (
            f"🛒 **SHOP & AFFILIATE**\n\n"
            f"💰 **Poin Anda:** `{points}`\n\n"
            f"🔗 **Link Bagikan Anda:**\n`{ref_link}`\n\n"
            f"*Bagikan link di atas ke teman/grup. Setiap 1 orang baru yang menekan Start = +1 Poin.*"
        )
        btns = [
            [Button.inline("💎 Tukar VIP 1 Jam (10 Poin)", b"buy_vip_1h")],
            [Button.inline("💎 Tukar VIP 30 Hari (1000 Poin)", b"buy_vip_30d")],
            [Button.inline("🔙 Kembali", b"menu_back")]
        ]
        await event.edit(text_shop, buttons=btns)
        
    elif data == b"menu_back":
        user = await event.get_sender()
        is_prem = role in ['vip', 'admin']
        c, s = "✅", "❌"
        caption = (
            f"**Halo {getattr(user, 'first_name', 'User')}!** 👋\n\n"
            f"**[ INFORMASI AKUN ]**\n"
            f"👤 **Status Role:** `{role.upper()}`\n\n"
            f"**[ FITUR AKSES ]**\n"
            f"🎵 Play Musik & Video : {c}\n"
            f"🔍 Pencarian YouTube : {c}\n"
            f"⏱ Durasi Tanpa Batas : {c if is_prem else s}\n"
            f"💾 File Media >100MB : {c if is_prem else s}\n"
            f"🔁 Loop Auto-Play : {c if is_prem else s}\n\n"
            f"Gunakan tombol di bawah untuk navigasi."
        )
        me = await bot.get_me()
        await event.edit(caption, buttons=start_buttons(me.username))

# TRANSAKSI PEMBELIAN VIP
@bot.on(events.CallbackQuery(pattern=b"buy_vip_.*"))
async def buy_vip(event):
    data = event.data.decode()
    user_id = event.sender_id
    u_data = await get_user_full(user_id)
    points = u_data[2]
    
    cost = 10 if data == "buy_vip_1h" else 1000
    duration_sec = 3600 if data == "buy_vip_1h" else 2592000
    dur_str = "1 Jam" if cost == 10 else "30 Hari"
        
    if points < cost:
        me = await bot.get_me()
        # Nilai query "url" dan "text" di-encode dengan benar (sebelumnya
        # ditulis mentah tanpa urlencode, yang berisiko dibaca keliru oleh
        # parser t.me/share/url karena mengandung "?" dan "&" di dalamnya).
        btns_row = []
        if me.username:
            ref_link = f"https://t.me/{me.username}?start=ref_{user_id}"
            share_url = "https://t.me/share/url?" + urlencode({"url": ref_link, "text": "Ayo coba bot musik ini!"})
            share_btn = _safe_url_button("↗️ Bagikan & Dapatkan Poin", share_url)
            if share_btn:
                btns_row.append([share_btn])
        btns_row.append([Button.inline("🔙 Kembali ke Shop", b"menu_shop")])
        btns = btns_row
        return await event.edit(
            f"❌ **Poin Tidak Cukup!**\n\n"
            f"Anda butuh {cost} poin untuk VIP {dur_str}, tapi Anda hanya memiliki **{points} poin**.\n\n"
            f"Bagikan bot ini ke teman atau grup menggunakan tombol di bawah untuk mendapatkan lebih banyak poin.", 
            buttons=btns
        )
        
    # Potong poin & aktifkan VIP dalam satu operasi atomik (mencegah user
    # yang klik tombol dua kali dengan cepat lolos membeli VIP 2x dengan
    # poin yang sama -- celah race condition pada versi lama).
    success, new_points = await try_purchase_vip(user_id, cost, duration_sec)
    if not success:
        return await event.answer("❌ Poin tidak cukup (mungkin sudah terpakai di transaksi lain).", alert=True)

    await event.answer(f"✅ Berhasil membeli VIP {dur_str}! Sisa Poin: {new_points}", alert=True)
    
    # Kembali ke Shop otomatis untuk melihat saldo yang berkurang
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start=ref_{user_id}"
    text_shop = (f"🛒 **SHOP & AFFILIATE**\n\n💰 **Poin Anda:** `{new_points}`\n\n🔗 **Link Bagikan Anda:**\n`{ref_link}`")
    btns = [[Button.inline("💎 Tukar VIP 1 Jam (10 Poin)", b"buy_vip_1h")], [Button.inline("💎 Tukar VIP 30 Hari (1000 Poin)", b"buy_vip_30d")], [Button.inline("🔙 Kembali", b"menu_back")]]
    await event.edit(text_shop, buttons=btns)
