import re
import os
import asyncio
from telethon import events, Button
from core.bot import bot
import config
from database.db import get_all_users, update_user, delete_user, add_or_get_user, get_user_full

# --- TAMPILAN 1: DASHBOARD UTAMA ---
def generate_admin_buttons(users, page=0):
    buttons = []
    start = page * 5
    end = start + 5
    
    for u in users[start:end]:
        uid, uname, role, status = u
        display_name = (uname[:12] + '..') if len(uname) > 15 else uname
        r_sym = "👑 VIP" if role == 'vip' else ("🛠 Admin" if role == 'admin' else "👤 Biasa")
        s_sym = "🔴 BANNED" if status == 'banned' else "🟢"
        buttons.append([Button.inline(f"{display_name} | {r_sym} | {s_sym}", f"adm_info_{uid}".encode())])
            
    nav = []
    if page > 0: nav.append(Button.inline("⬅️ Prev", f"admpg_{page-1}".encode()))
    nav.append(Button.inline("Tutup ❌", b"adm_close"))
    if end < len(users): nav.append(Button.inline("Next ➡️", f"admpg_{page+1}".encode()))
    if nav: buttons.append(nav)
    return buttons

# --- TAMPILAN 2: PENGATURAN USER ---
def generate_role_buttons(uid, status, target_role):
    buttons = []
    if uid == config.ADMIN_ID:
        buttons.append([Button.inline("👑 Akun Owner Utama", b"ignore")])
    else:
        buttons.append([Button.inline("➕ Tambah Poin", f"adm_addp_{uid}".encode())])
        if target_role != 'admin':
            buttons.append([Button.inline("🛠 Jadikan Admin", f"adm_setrole_admin_{uid}".encode())])
            buttons.append([Button.inline("👑 Jadikan VIP", f"adm_setrole_vip_{uid}".encode()), 
                            Button.inline("👤 Jadikan Biasa", f"adm_setrole_user_{uid}".encode())])
            aksi = []
            if status == 'active': aksi.append(Button.inline("🔨 Ban User", f"adm_ban_{uid}".encode()))
            else: aksi.append(Button.inline("♻️ Unban User", f"adm_unban_{uid}".encode()))
            aksi.append(Button.inline("🗑 Hapus Data", f"adm_del_{uid}".encode()))
            buttons.append(aksi)
        else:
            buttons.append([Button.inline("👤 Cabut Admin (Jadikan Biasa)", f"adm_setrole_user_{uid}".encode())])
    buttons.append([Button.inline("🔙 Kembali ke Dashboard", b"adm_back")])
    return buttons

# --- HANDLER: /admin ---
@bot.on(events.NewMessage(pattern=r'^/admin$'))
async def admin_panel(event):
    user_id = event.sender_id
    role, _, _ = await add_or_get_user(user_id, "Unknown")
    if user_id != config.ADMIN_ID and role != 'admin': 
        return await event.respond("❌ Akses ditolak.")
    users = await get_all_users()
    if not users: return await event.respond("Database kosong.")
    await event.respond("**🛠 ADMIN DASHBOARD**", buttons=generate_admin_buttons(users, 0))

# --- HANDLER: CALLBACK ---
@bot.on(events.CallbackQuery(pattern=re.compile(b"^(adm_|admpg_)")))
async def admin_callback(event):
    user_id = event.sender_id
    role, _, _ = await add_or_get_user(user_id, "Unknown")
    if user_id != config.ADMIN_ID and role != 'admin': return
    
    data_str = event.data.decode()
    parts = data_str.split("_")
    
    if data_str == "adm_close": return await event.delete()
    if data_str == "adm_back":
        await event.delete()
        return await bot.send_message(event.chat_id, "**🛠 ADMIN DASHBOARD**", buttons=generate_admin_buttons(await get_all_users(), 0))
    if data_str.startswith("admpg_"):
        return await event.edit("**🛠 ADMIN DASHBOARD**", buttons=generate_admin_buttons(await get_all_users(), int(parts[1])))

    uid = None
    if parts[1] == "addp": uid = int(parts[2])
    elif parts[1] == "setrole" and len(parts) >= 4: uid = int(parts[3])
    elif len(parts) >= 3 and parts[2].isdigit(): uid = int(parts[2])
    if not uid: return 

    # --- FITUR TAMBAH POIN (FLOW: KLIK -> HILANG -> TANYA) ---
    if parts[1] == "addp":
        # 1. Ambil & Hapus tabel profil SEGERA setelah diklik
        tabel_msg = await event.get_message()
        try: await tabel_msg.delete()
        except: pass
        
        # 2. Mulai konversasi permintaan poin
        async with bot.conversation(event.chat_id) as conv:
            prompt = await conv.send_message(f"✨ **TAMBAH POIN**\nUser ID: `{uid}`\n\nKetik jumlah poin yang ingin ditambahkan:")
            try:
                msg = await conv.get_response(timeout=30)
                if msg.text and msg.text.isdigit():
                    amount = int(msg.text)
                    u_info = await get_user_full(uid)
                    new_pts = u_info[2] + amount
                    await update_user(uid, "points", new_pts)
                    
                    await conv.send_message(f"✅ Berhasil! `{uid}` sekarang memiliki **{new_pts}** poin.")
                    try: await bot.send_message(uid, f"🎁 **Poin Masuk!**\nOwner menambah **{amount}** poin ke akun Anda.")
                    except: pass
                else:
                    await conv.send_message("❌ Batal. Masukkan angka saja.")
            except asyncio.TimeoutError:
                await conv.send_message("🕒 Waktu habis.")
            finally:
                try: await prompt.delete()
                except: pass
        return

    # --- INFO USER ---
    if parts[1] == "info":
        users = await get_all_users()
        target = next((u for u in users if u[0] == uid), None)
        if not target: return await event.answer("User tidak ditemukan!")
        u_info = await get_user_full(uid)
        text = f"👤 **PROFIL USER**\n\n**Nama:** `{target[1]}`\n**ID:** `{uid}`\n**Role:** `{target[2].upper()}`\n**Poin:** `{u_info[2]}`\n**Status:** `{'BANNED' if target[3] == 'banned' else 'AKTIF'}`"
        
        await event.delete()
        photo = await bot.download_profile_photo(uid, file=f"downloads/pfp_{uid}.jpg")
        if not photo or not os.path.exists(photo): photo = "template.jpg"
        await bot.send_file(event.chat_id, file=photo, caption=text, buttons=generate_role_buttons(uid, target[3], target[2]))
        if "downloads/" in str(photo): os.remove(photo)
        return

    # --- ACTION ROLE/BAN ---
    action = parts[1]
    if action == "setrole":
        if uid == config.ADMIN_ID: return await event.answer("Dilarang!")
        await update_user(uid, "role", parts[2])
        await event.answer(f"Role diperbarui!")
    elif action in ["ban", "unban", "del"]:
        if uid == config.ADMIN_ID: return
        if action == "ban": await update_user(uid, "status", "banned")
        elif action == "unban": await update_user(uid, "status", "active")
        elif action == "del": 
            await delete_user(uid)
            await event.delete()
            return await bot.send_message(event.chat_id, "**🛠 ADMIN DASHBOARD**", buttons=generate_admin_buttons(await get_all_users(), 0))

    # Auto Refresh
    u_info = await get_user_full(uid)
    try: await event.edit(buttons=generate_role_buttons(uid, u_info[1], u_info[0]))
    except: pass
