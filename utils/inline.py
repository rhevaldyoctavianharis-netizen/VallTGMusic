from telethon import Button
import re
import config

# Username Telegram yang valid: 5-32 karakter, huruf/angka/underscore,
# tidak diawali angka. Dipakai untuk memvalidasi nilai dari .env sebelum
# dijadikan URL tombol.
_USERNAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,31}$")


def _safe_url_button(text: str, url: str):
    """
    Bungkus Button.url dengan validasi. Kalau URL hasil rakitan tidak
    berformat wajar, kembalikan None (tombol dilewati) alih-alih
    membiarkan Telegram menolak SELURUH pesan dengan
    ButtonUrlInvalidError -- yang sebelumnya bikin foto /start gagal
    terkirim total hanya gara-gara satu tombol bermasalah.
    """
    if not url:
        return None
    if url.startswith("tg://"):
        return Button.url(text, url)
    if url.startswith("https://t.me/") or url.startswith("http://t.me/"):
        # Path setelah t.me/ harus terlihat seperti username/invite link,
        # bukan kosong, bukan angka mentah (chat_id), bukan mengandung spasi.
        path = url.split("t.me/", 1)[1]
        path_no_query = path.split("?", 1)[0]
        if not path_no_query or " " in path or path_no_query.lstrip("-").isdigit():
            return None
        return Button.url(text, url)
    if url.startswith("https://") or url.startswith("http://"):
        return Button.url(text, url)
    return None


def start_buttons(bot_username: str):
    rows = []

    add_group_btn = _safe_url_button(
        "➕ Add Me to Group",
        f"https://t.me/{bot_username}?startgroup=true" if bot_username else "",
    )
    if add_group_btn:
        rows.append([add_group_btn])

    rows.append([Button.inline("📖 Cara Penggunaan", b"menu_help"), Button.inline("🛒 Shop & Affiliate", b"menu_shop")])

    # CREDIT_CHANNEL bersifat opsional dan formatnya bebas di .env
    # ("@nama", "nama", atau link https:// penuh). Semua bentuk dirakit
    # jadi URL lalu divalidasi lewat _safe_url_button sebelum dipakai --
    # kalau nilainya kosong atau tidak valid (misalnya chat_id numerik),
    # tombolnya cukup dilewati, bot tetap jalan normal.
    credit = (config.CREDIT_CHANNEL or "").strip()
    if credit:
        if credit.startswith("@"):
            credit_url = f"https://t.me/{credit[1:]}"
        elif credit.startswith("http://") or credit.startswith("https://") or credit.startswith("tg://"):
            credit_url = credit
        else:
            credit_url = f"https://t.me/{credit}"
        credit_btn = _safe_url_button("📢 Channel Info", credit_url)
        if credit_btn:
            rows.append([credit_btn])

    # Tautan source code (GitHub). Bisa diganti lewat env GITHUB_URL.
    github_btn = _safe_url_button("💻 Source Code (GitHub)", (getattr(config, "GITHUB_URL", "") or "").strip())
    if github_btn:
        rows.append([github_btn])

    return rows

def get_progress_bar(current: float, total: float) -> str:
    length = 15
    if total <= 0: return "00:00 🔘" + "▬" * (length - 1) + " 00:00"
    percent = current / total
    pos = int(length * percent)
    if pos >= length: pos = length - 1
    bar = "▬" * pos + "🔘" + "▬" * (length - pos - 1)
    cur_m, cur_s = divmod(int(current), 60)
    tot_m, tot_s = divmod(int(total), 60)
    return f"{cur_m:02d}:{cur_s:02d} {bar} {tot_m:02d}:{tot_s:02d}"

def stream_controls(current=0, total=0, is_loop=False, role='user', is_paused=False):
    loop_text = "🔁 Loop: ON 🟢" if is_loop else "🔁 Loop: OFF 🔴"
    play_pause_btn = Button.inline("▶️ Resume", b"ctrl_resume") if is_paused else Button.inline("⏸ Pause", b"ctrl_pause")
    
    btns = [
        [Button.inline(get_progress_bar(current, total), b"ctrl_ignore")],
        [play_pause_btn, Button.inline("⏭ Next Music", b"ctrl_skip_q")],
        [Button.inline("⏩ Skip +5s", b"ctrl_next"), Button.inline("⏹ Stop", b"ctrl_stop")]
    ]
    if role in ['vip', 'admin'] or role == 'owner':
        btns.append([Button.inline(loop_text, b"ctrl_loop")])
    return btns

def search_buttons(page: int, total_results: int):
    buttons = []
    row_numbers = []
    for i in range(total_results):
        row_numbers.append(Button.inline(str(i + 1), data=f"ytsel_{i}".encode()))
    if row_numbers: buttons.append(row_numbers)
    nav_row = []
    if page > 0: nav_row.append(Button.inline("⬅️ Prev", data=b"ytnav_prev"))
    nav_row.append(Button.inline("❌ Batal", data=b"ytnav_cancel"))
    if total_results == 5: nav_row.append(Button.inline("Next ➡️", data=b"ytnav_next"))
    buttons.append(nav_row)
    return buttons

def film_buttons(page: int, total_results: int):
    buttons = []
    row_numbers = []
    for i in range(total_results):
        row_numbers.append(Button.inline(str(i + 1), data=f"flmsel_{i}".encode()))
    if row_numbers: buttons.append(row_numbers)
    nav_row = []
    if page > 0: nav_row.append(Button.inline("⬅️ Prev", data=b"flmnav_prev"))
    nav_row.append(Button.inline("❌ Tutup", data=b"flmnav_cancel"))
    if total_results == 5: nav_row.append(Button.inline("Next ➡️", data=b"flmnav_next"))
    buttons.append(nav_row)
    return buttons

def queue_buttons(queue_data):
    buttons = []
    row = []
    for i, item in enumerate(queue_data):
        queue_id = item[0]
        row.append(Button.inline(f"❌ {i+1}", data=f"delq_{queue_id}".encode()))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([Button.inline("🗑 Bersihkan Semua", b"delq_all")])
    buttons.append([Button.inline("Tutup", b"delq_close")])
    return buttons

def listplay_buttons(streams, page, total_pages):
    buttons = []
    for stream in streams:
        chat_id = stream[0]
        buttons.append([
            Button.inline(f"🛑 Stop: {chat_id}", data=f"fstop_{chat_id}".encode()),
            Button.inline(f"🚫 Stop & Banned", data=f"fban_{chat_id}".encode())
        ])
    nav = []
    if page > 0: nav.append(Button.inline("⬅️ Prev", data=f"lpnav_{page-1}".encode()))
    nav.append(Button.inline("❌ Tutup", data=b"lpnav_close"))
    if page < total_pages - 1: nav.append(Button.inline("Next ➡️", data=f"lpnav_{page+1}".encode()))
    if nav: buttons.append(nav)
    return buttons

def listban_buttons(banned_groups, page, total_pages):
    buttons = []
    for b in banned_groups:
        chat_id = b[0]
        buttons.append([Button.inline(f"✅ Unbanned: {chat_id}", data=f"unban_{chat_id}".encode())])
    nav = []
    if page > 0: nav.append(Button.inline("⬅️ Prev", data=f"lbnav_{page-1}".encode()))
    nav.append(Button.inline("❌ Tutup", data=b"lbnav_close"))
    if page < total_pages - 1: nav.append(Button.inline("Next ➡️", data=f"lbnav_{page+1}".encode()))
    if nav: buttons.append(nav)
    return buttons

def ban_msg_btn(admin_id):
    if not admin_id:
        return None
    return [[Button.url("👨‍💻 Hubungi Admin", f"tg://openmessage?user_id={admin_id}")]]
