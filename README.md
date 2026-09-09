# MusicBot — Telegram Voice Chat Music Bot

Bot musik Telegram berbasis Telethon (bot) + Telethon Userbot + PyTgCalls
(streaming Voice Chat). Sudah dioptimalkan agar hemat sumber daya (lihat
`PERUBAHAN.md`) dan portable di Linux/Windows/macOS.

## Kebutuhan
- Python **3.9 atau lebih baru** (disarankan 3.10+)
- **ffmpeg** terpasang di sistem
- **Deno** (atau Node.js 20+) — dibutuhkan `yt-dlp` untuk ekstraksi YouTube
  yang stabil (lihat catatan di bagian Troubleshooting)
- Akun Telegram untuk userbot (akun pribadi, bukan bot) yang akan join Voice Chat
- Bot Telegram dari @BotFather

## 🚀 Setup Cepat di VPS Linux (Ubuntu/Debian/CentOS/dll)

```bash
# 1. Upload/clone source ke VPS, lalu masuk ke foldernya
cd MusicBot_Optimized

# 2. Jalankan skrip setup otomatis (install ffmpeg, Deno, venv, dependensi)
chmod +x setup_vps.sh
./setup_vps.sh

# 3. Isi kredensial
nano .env

# 4. Jalankan bot (untuk tes manual dulu)
source venv/bin/activate
python3 main.py
```

Kalau bot berjalan normal (`🚀 MusicBot Professional Berhasil Berjalan!`
muncul di terminal tanpa error), tekan `Ctrl+C` lalu lanjut ke bagian
**Auto-Start & Auto-Restart** di bawah supaya bot jalan permanen di
background.

## Isi `.env`
Semua variabel dijelaskan di `.env.example`. Ringkasnya:

| Variabel | Wajib? | Dari mana |
|---|---|---|
| `API_ID`, `API_HASH` | ✅ | https://my.telegram.org |
| `BOT_TOKEN` | ✅ | @BotFather |
| `SESSION_STRING` | ✅ | Script Telethon StringSession (caranya ada di `.env.example`) |
| `ADMIN_ID` | ✅ | ID Telegram-mu sendiri (cek via @userinfobot) |
| `CREDIT_CHANNEL` | ❌ opsional | Link channel-mu |
| `FSUB_CHANNEL` | ❌ opsional | Username channel wajib-join |

## 🔁 Auto-Start & Auto-Restart (systemd)

Ini bikin bot **otomatis jalan lagi kalau VPS reboot** dan **otomatis
restart kalau bot crash** — jadi tidak perlu login SSH tiap kali mau
menyalakan bot.

```bash
# 1. Salin & sesuaikan template service
sudo cp musicbot.service /etc/systemd/system/musicbot.service
sudo nano /etc/systemd/system/musicbot.service
#    -> Sesuaikan "User", "WorkingDirectory", dan "ExecStart"
#       dengan lokasi folder project & user VPS-mu.

# 2. Aktifkan & jalankan
sudo systemctl daemon-reload
sudo systemctl enable musicbot      # auto-start saat boot
sudo systemctl start musicbot       # jalankan sekarang

# 3. Cek status & log
sudo systemctl status musicbot
tail -f /var/log/musicbot.log       # log real-time

# Perintah lain yang berguna:
sudo systemctl restart musicbot     # restart manual
sudo systemctl stop musicbot        # matikan
```

## 📤 Membagikan Source Code

Kalau mau di-share lewat Git (GitHub/GitLab):

```bash
git init
git add .
git commit -m "Initial commit"
```

File `.gitignore` sudah disiapkan agar `.env`, file sesi, database, dan
folder `downloads/` **tidak ikut ter-commit** — jadi aman dibagikan tanpa
membocorkan kredensial siapa pun yang memakainya. Setiap orang yang
clone source ini tinggal mengulangi langkah **Setup Cepat** di atas
dengan `.env` milik mereka sendiri.

⚠️ Kalau repo akan di-push ke GitHub **public**, jangan pernah commit
`.env` yang sudah terisi. Cek dulu dengan `git status` sebelum commit
pertama untuk memastikan `.env` tidak ikut ter-tracking.

## Troubleshooting

**Warning `No supported JavaScript runtime could be found` dari yt-dlp:**
Install Deno (sudah otomatis dipasang oleh `setup_vps.sh`). Kalau warning
masih muncul setelah setup, jalankan `deno --version` untuk memastikan
Deno benar-benar terbaca di PATH sesi terminal yang menjalankan bot
(kalau lewat systemd, pastikan `ExecStart` di `musicbot.service` memakai
python dari `venv/bin/python3`, bukan python sistem, dan PATH sistem service
mencakup lokasi `deno`).

**`ValueError: Could not find the input entity` dari userbot:**
Pastikan akun userbot sudah benar-benar jadi member di grup tempat bot
dipakai. Lihat juga catatan di `PERUBAHAN.md` bagian 9.

**Bot jalan tapi tidak bisa masuk Voice Chat:**
Pastikan akun userbot (bukan akun bot) yang punya izin/sudah join sebagai
member biasa di grup tersebut, dan grup tersebut sudah punya Voice Chat
aktif.

## Struktur Project
Lihat `PERUBAHAN.md` untuk detail lengkap optimasi & perbaikan yang sudah
diterapkan pada codebase ini.
