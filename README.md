<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7F00FF,100:E100FF&height=220&section=header&text=VallTgMusic%20New&fontSize=58&fontColor=ffffff&fontAlignY=38&desc=Telegram%20Voice%20Chat%20Music%20Bot%20%E2%80%A2%20Cepat%20%E2%80%A2%20Hemat%20%E2%80%A2%20Siap%20Deploy&descAlignY=60&descSize=18" alt="VallTgMusic New" width="100%"/>

<a href="https://github.com/rhevaldyoctavianharis-netizen/VallTGMusic">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=20&pause=1200&color=C77DFF&center=true&vCenter=true&width=620&lines=Streaming+musik+%26+video+di+Voice+Chat;Hemat+resource%2C+portable+di+semua+OS;Auto-restart+dengan+systemd;Deploy+ke+Heroku+dalam+1+klik" alt="Typing SVG" />
</a>

<br/>

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-Bot%20%2B%20Userbot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![PyTgCalls](https://img.shields.io/badge/PyTgCalls-Voice%20Chat-7F00FF?style=for-the-badge)
![yt-dlp](https://img.shields.io/badge/yt--dlp-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)

<br/>

[![Deploy ke Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rhevaldyoctavianharis-netizen/VallTGMusic)
<a href="https://t.me/OneDotOneBot"><img src="https://img.shields.io/badge/%F0%9F%8E%A7%20Coba%20Bot-@OneDotOneBot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Coba Bot @OneDotOneBot" height="28"/></a>

<br/>

[✨ Fitur](#-fitur) •
[🤖 Coba Bot](#-coba-bot) •
[📋 Kebutuhan](#-kebutuhan) •
[🚀 Deploy Heroku](#-deploy-ke-heroku) •
[🖥️ Setup VPS](#️-setup-cepat-di-vps-linux) •
[🔁 Auto-Start](#-auto-start--auto-restart-systemd) •
[🧯 Troubleshooting](#-troubleshooting) •
[🤝 Kontak](#-kolaborasi--kontak) •
[👤 Kredit](#-kredit)

</div>

---

## ✨ Fitur

<table>
<tr>
<td width="33%" valign="top">

### 🎧 Voice Chat
Streaming musik langsung ke **Voice Chat** grup lewat PyTgCalls, dengan akun userbot yang bergabung otomatis.

</td>
<td width="33%" valign="top">

### ⚡ Hemat Resource
Sudah dioptimalkan agar ringan di CPU, RAM, dan disk sehingga nyaman dijalankan di VPS kecil.

</td>
<td width="33%" valign="top">

### 🌍 Portable
Berjalan di **Linux, Windows, dan macOS**. Untuk VPS tersedia skrip setup otomatis.

</td>
</tr>
<tr>
<td width="33%" valign="top">

### ▶️ YouTube Stabil
Ekstraksi lewat **yt-dlp** dengan JavaScript runtime (**Deno** atau **Node.js**) agar tidak mudah kena bot-check.

</td>
<td width="33%" valign="top">

### 🔁 Selalu Hidup
Template **systemd** membuat bot menyala saat VPS reboot dan restart otomatis bila crash.

</td>
<td width="33%" valign="top">

### ☁️ Siap Deploy
Tombol **Deploy ke Heroku** dengan formulir variabel, plus `Procfile` dan `app.json` yang sudah disiapkan.

</td>
</tr>
</table>

Opsi tambahan lewat `.env`: **`FSUB_CHANNEL`** (wajib join channel) dan **`CREDIT_CHANNEL`** (kredit channel Anda).

---

## 🤖 Coba Bot

Ingin melihat hasilnya dulu sebelum deploy sendiri? Coba langsung bot demonya:

<div align="center">

<a href="https://t.me/OneDotOneBot"><img src="https://img.shields.io/badge/Buka%20di%20Telegram-@OneDotOneBot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Buka @OneDotOneBot"/></a>

</div>

---

## 📋 Kebutuhan

| Komponen | Keterangan |
|---|---|
| 🐍 **Python** | **3.9 atau lebih baru** (disarankan 3.10+) |
| 🎞️ **ffmpeg** | Terpasang di sistem |
| 🦕 **Deno** atau **Node.js 20+** | Dibutuhkan `yt-dlp` untuk ekstraksi YouTube yang stabil |
| 👤 **Akun userbot** | Akun Telegram pribadi (bukan bot) yang akan join Voice Chat |
| 🤖 **Bot Telegram** | Dibuat lewat [@BotFather](https://t.me/BotFather) |

---

## ⚙️ Konfigurasi `.env`

Salin file contoh menjadi `.env`, lalu isi nilainya:

```bash
# Linux / macOS
cp .env.example .env

# Windows (CMD)
copy .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Buka `.env` dengan editor favorit Anda (`nano .env` di Linux/macOS, atau Notepad di Windows). Semua variabel dijelaskan di `.env.example`. Ringkasnya:

| Variabel | Wajib | Dari mana |
|---|:---:|---|
| `API_ID`, `API_HASH` | ✅ | [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | ✅ | [@BotFather](https://t.me/BotFather) |
| `SESSION_STRING` | ✅ | Script Telethon StringSession (caranya ada di `.env.example`) |
| `ADMIN_ID` | ✅ | ID Telegram Anda sendiri (cek via [@userinfobot](https://t.me/userinfobot)) |
| `CREDIT_CHANNEL` | ➖ | Link channel Anda |
| `FSUB_CHANNEL` | ➖ | Username channel wajib-join |

### 🔑 Dapatkan `SESSION_STRING`

Cara termudah: ambil string session lewat bot generator berikut.

<div align="center">

<a href="https://t.me/ssgenduabot"><img src="https://img.shields.io/badge/Generate%20String%20Session-@ssgenduabot-7F00FF?style=for-the-badge&logo=telegram&logoColor=white" alt="Generate String Session @ssgenduabot"/></a>

</div>

1. Buka [@ssgenduabot](https://t.me/ssgenduabot) lalu ikuti petunjuknya.
2. Salin string session yang diberikan ke `SESSION_STRING` di `.env`.

Alternatif tanpa bot: buat sendiri dengan Telethon `StringSession`, caranya ada di `.env.example`.

> 🔒 **Penting:** `SESSION_STRING` memberi akses penuh ke akun Telegram, jadi perlakukan seperti password. Disarankan memakai **akun userbot cadangan**, bukan akun utama, dan jangan pernah membagikan `SESSION_STRING` maupun `BOT_TOKEN` ke siapa pun.

---

## 🚀 Deploy ke Heroku

> Heroku tidak memakai file `.env`. Semua pengaturan dibaca dari **Config Vars**, dan tombol Deploy akan menampilkan formulirnya.

**1.** Siapkan `SESSION_STRING` lebih dulu, lewat [@ssgenduabot](https://t.me/ssgenduabot) atau buat sendiri di komputer Anda (bukan di Heroku).

**2.** Tekan tombol di bawah, lalu isi formulir:

[![Deploy ke Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rhevaldyoctavianharis-netizen/VallTGMusic)

| Variabel | Wajib | Keterangan |
|---|:---:|---|
| `API_ID` | ✅ | Dari [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | Dari [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | ✅ | Dari [@BotFather](https://t.me/BotFather) |
| `SESSION_STRING` | ✅ | Telethon StringSession akun userbot |
| `ADMIN_ID` | ✅ | ID Telegram Anda (owner) |
| `CREDIT_CHANNEL` | ➖ | Contoh: `https://t.me/channelanda` |
| `FSUB_CHANNEL` | ➖ | `@channel` wajib join (kosong = nonaktif) |

Variabel lain bisa diubah di **Settings → Config Vars** setelah deploy.

<details>
<summary><b>⌨️ Deploy lewat Heroku CLI</b></summary>

```bash
heroku create nama-app-anda
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... SESSION_STRING=... ADMIN_ID=...
git push heroku main
heroku ps:scale worker=1
heroku logs --tail
```

</details>

<details>
<summary><b>⚠️ Batasan Heroku yang perlu diketahui</b></summary>

- **Penyimpanan sementara.** Database, file sesi, dan folder `downloads/` hilang saat dyno restart (sekitar 24 jam sekali). Untuk data permanen, gunakan penyimpanan eksternal.
- **`localhost` tidak bisa dipakai.** Layanan eksternal harus punya alamat publik.
- **Cookies browser tidak ada.** Server tidak punya browser, gunakan `YT_COOKIES_FILE` bila perlu.
- **Jangan commit rahasia.** `.env`, `SESSION_STRING`, dan API key tidak boleh masuk repo publik.

</details>

---

## 🖥️ Setup Cepat di VPS Linux

Berlaku untuk Ubuntu, Debian, CentOS, dan sejenisnya.

```bash
# 1. Upload/clone source ke VPS, lalu masuk ke foldernya
cd VallTGMusic

# 2. Jalankan skrip setup otomatis (pasang ffmpeg, Deno, venv, dependensi)
chmod +x setup_vps.sh
./setup_vps.sh

# 3. Salin contoh konfigurasi, lalu isi kredensial
cp .env.example .env
nano .env

# 4. Jalankan bot (tes manual dulu)
source venv/bin/activate
python3 main.py
```

Jika terminal menampilkan `🚀 MusicBot Professional Berhasil Berjalan!` tanpa error, tekan `Ctrl+C` lalu lanjut ke bagian **Auto-Start** agar bot jalan permanen di background.

---

## 🔁 Auto-Start & Auto-Restart (systemd)

Bot otomatis menyala lagi saat VPS reboot dan restart sendiri bila crash, jadi tidak perlu login SSH tiap kali.

```bash
# 1. Salin & sesuaikan template service
sudo cp musicbot.service /etc/systemd/system/musicbot.service
sudo nano /etc/systemd/system/musicbot.service
#    → sesuaikan "User", "WorkingDirectory", dan "ExecStart"
#      dengan lokasi folder project & user VPS Anda

# 2. Aktifkan & jalankan
sudo systemctl daemon-reload
sudo systemctl enable musicbot      # auto-start saat boot
sudo systemctl start musicbot       # jalankan sekarang

# 3. Cek status & log
sudo systemctl status musicbot
tail -f /var/log/musicbot.log       # log real-time
```

| Perintah | Fungsi |
|---|---|
| `sudo systemctl restart musicbot` | Restart manual |
| `sudo systemctl stop musicbot` | Matikan bot |
| `sudo systemctl status musicbot` | Lihat status |

---

## 🧯 Troubleshooting

<details>
<summary><b>Warning <code>No supported JavaScript runtime could be found</code> dari yt-dlp</b></summary>

Pasang **Deno** (sudah otomatis dipasang oleh `setup_vps.sh`) atau Node.js 20+. Jika warning masih muncul:

- Jalankan `deno --version` untuk memastikan Deno terbaca di PATH sesi yang menjalankan bot.
- Jika lewat systemd, pastikan `ExecStart` di `musicbot.service` memakai python dari `venv/bin/python3` (bukan python sistem), dan PATH service mencakup lokasi `deno`.

</details>

<details>
<summary><b>Error <code>ValueError: Could not find the input entity</code> dari userbot</b></summary>

Pastikan akun userbot sudah benar-benar menjadi **member** di grup tempat bot dipakai.

</details>

<details>
<summary><b>Bot jalan tapi tidak bisa masuk Voice Chat</b></summary>

Pastikan akun **userbot** (bukan akun bot) sudah join sebagai member biasa di grup tersebut, dan grup sudah punya **Voice Chat yang aktif**.

</details>

---

## 📤 Membagikan Source Code dengan Aman

```bash
git init
git add .
git commit -m "Initial commit"
```

`.gitignore` sudah disiapkan agar `.env`, file sesi, database, dan folder `downloads/` **tidak ikut ter-commit**. Siapa pun yang clone cukup mengulangi langkah setup dengan `.env` miliknya sendiri.

> ⚠️ Jika repo akan di-push ke GitHub **publik**, jangan pernah commit `.env` yang sudah terisi. Jalankan `git status` sebelum commit pertama untuk memastikan `.env` tidak ikut ter-tracking.

---

## 🤝 Kolaborasi & Kontak

Perlu kolaborasi, kontak, atau yang lainnya? Kunjungi website portofolio saya:

<div align="center">

<a href="https://rhevaldy.my.id"><img src="https://img.shields.io/badge/Portofolio-rhevaldy.my.id-E100FF?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Portofolio rhevaldy.my.id"/></a>
<a href="https://t.me/rapaldy"><img src="https://img.shields.io/badge/Telegram-@rapaldy-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram @rapaldy"/></a>

</div>

---

## 👤 Kredit

<div align="center">

| | |
|---|---|
| 👨‍💻 **Pembuat** | [@rapaldy](https://t.me/rapaldy) |
| 📢 **Channel** | [@youlittleboy](https://t.me/youlittleboy) |

<a href="https://t.me/rapaldy"><img src="https://img.shields.io/badge/Chat%20Pembuat-@rapaldy-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram @rapaldy"/></a>
<a href="https://t.me/youlittleboy"><img src="https://img.shields.io/badge/Join%20Channel-@youlittleboy-7F00FF?style=for-the-badge&logo=telegram&logoColor=white" alt="Channel @youlittleboy"/></a>

</div>

Mau pakai atau modifikasi proyek ini? Silakan, tetapi mohon **pertahankan kredit** di atas. Terima kasih! 🙏

---

<div align="center">

### 💜 Dibuat oleh [@rapaldy](https://t.me/rapaldy) • Channel [@youlittleboy](https://t.me/youlittleboy)

**⭐ Beri bintang jika proyek ini bermanfaat!**

<br/>

![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![Made in Indonesia](https://img.shields.io/badge/Made%20in-Indonesia-red?style=flat-square)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:E100FF,100:7F00FF&height=100&section=footer" width="100%" alt=""/>

</div>
