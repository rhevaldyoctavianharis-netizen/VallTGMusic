# Catatan Perubahan — Optimasi Resource MusicBot

## 1. Database (`database/db.py`)
- Sebelumnya: setiap fungsi membuka koneksi SQLite baru (`aiosqlite.connect`) —
  sangat boros karena progress bar memanggil DB beberapa kali/detik per grup aktif.
- Sekarang: satu koneksi persisten dibuat sekali di `init_db()`, dipakai ulang
  oleh semua fungsi. Ditambah `PRAGMA journal_mode=WAL` dan
  `PRAGMA synchronous=NORMAL` agar baca/tulis bersamaan tidak saling mengunci
  dan lebih ringan ke disk.
- `update_user()` sekarang memvalidasi nama kolom lewat whitelist
  (`_ALLOWED_USER_FIELDS`) — menutup celah SQL injection dari interpolasi
  nama kolom.
- Fungsi baru `try_purchase_vip()` — potong poin & aktifkan VIP dalam satu
  statement SQL atomik (`UPDATE ... WHERE points >= ?`), menutup race condition
  saat tombol beli VIP diklik dua kali dengan cepat.
- Fungsi baru `get_all_referenced_media_files()` — dipakai oleh tugas
  pembersih file yatim (lihat poin 3).
- `close_db()` untuk menutup koneksi dengan rapi saat bot berhenti.

## 2. Progress bar diperlambat 1 detik → 5 detik (`plugins/bot/play.py`)
Progress bar musik tidak perlu update per detik. Interval 5 detik menurunkan
jumlah query DB dan panggilan `edit_message` ke Telegram API hingga 5x lipat,
sekaligus mengurangi risiko kena flood-wait dari Telegram saat banyak grup
streaming bersamaan.

## 3. File download yang tidak pernah dihapus (bug besar)
Sebelumnya file audio/video hasil download **tidak pernah dihapus** setelah
selesai diputar — folder `downloads/` akan terus membesar tanpa henti.
Sekarang file dihapus otomatis di semua titik transisi:
- `/stop`, skip ke lagu berikutnya, lagu diganti lewat `/play` baru
- Stream alami berakhir / bot keluar VC / di-kick
- Grup user dipaksa berhenti karena slot direbut VIP
- Admin force-stop / force-ban grup

Plus **tugas latar belakang baru** (`utils/cleanup.py`) yang jalan tiap 1 jam:
memindai `downloads/`, dan menghapus file berumur >6 jam yang sudah tidak
direferensikan oleh stream/antrean manapun. Ini jaring pengaman kalau bot
pernah crash di tengah proses sehingga pembersihan normal terlewat.

## 4. Fitur "Skip +5s" — dari blocking jadi async (`plugins/controls/stream_controls.py`)
Sebelumnya pakai `os.system(f"ffmpeg ...")` yang **memblokir seluruh event
loop bot** — semua grup lain ikut macet selama proses potong video berjalan.
Diganti dengan `asyncio.create_subprocess_exec` (pola yang sama seperti
`utils/media.py`). Juga memperbaiki bug: file yang sudah dipotong sekarang
benar-benar tercatat sebagai `current_media` yang sedang diputar (sebelumnya
DB masih menyimpan path file lama).

## 5. Render gambar `/start` dipindah ke thread (`plugins/bot/start.py`)
`generate_start_image()` memakai PIL secara sinkron (resize, render font,
encode JPEG) — kalau dipanggil langsung di event loop, ini memblokir seluruh
bot selama proses render. Sekarang dijalankan lewat `asyncio.to_thread`.

## 6. Cache status join channel FSUB (`utils/checker.py`)
Sebelumnya `GetParticipantRequest` (cek member channel) dipanggil ke Telegram
API pada **setiap** perintah (`/play`, `/queue`, dll). Sekarang di-cache 10
menit per user — status join jarang berubah, jadi jumlah panggilan API turun
drastis tanpa mengorbankan akurasi.

## 7. `main.py`
- `os.makedirs("downloads", exist_ok=True)` di awal agar folder selalu ada.
- Tugas pembersih file yatim dijalankan sebagai background task.
- Pakai `asyncio.run()` (bukan `get_event_loop().run_until_complete()` yang
  sudah deprecated) dan menutup koneksi DB dengan rapi lewat `close_db()`
  saat bot berhenti.

## 8. Perbaikan `ButtonUrlInvalidError` (`utils/inline.py`, `utils/checker.py`, `plugins/bot/start.py`)
Sebelumnya beberapa tombol (`Button.url`) dirakit langsung dari nilai `.env`
(`CREDIT_CHANNEL`) atau `me.username` tanpa validasi format. Kalau nilainya
tidak persis sesuai yang diterima Telegram (misalnya berupa chat_id numerik,
mengandung spasi, atau kosong), Telegram menolak **seluruh pesan** dengan
`ButtonUrlInvalidError` -- termasuk foto `/start` yang seharusnya terkirim.
Sekarang ada fungsi `_safe_url_button()` di `utils/inline.py` yang memvalidasi
setiap URL tombol sebelum dipakai; kalau tidak valid, tombolnya cukup
dilewati (bot tetap jalan normal) alih-alih membuat seluruh pengiriman pesan
gagal. Diterapkan pada tombol "Add Me to Group", "Channel Info", "Join
Channel" (FSUB), "Mulai Bot", dan tombol share/referral.

## 9. Perbaikan `ValueError: Could not find the input entity` (`plugins/bot/play.py`, `main.py`)
Sebelumnya pesan status sementara ("Memproses...", "Mengunduh...") dikirim
lewat akun **userbot** (`userbot.send_message`). Masalahnya, sesi userbot
belum tentu punya entity chat tersebut ter-cache di Telethon -- ini bisa
terjadi walau userbot sudah jadi member grup, kalau sesinya belum pernah
menerima update apa pun dari chat itu. Akibatnya Telethon gagal total
dengan `ValueError: Could not find the input entity`.
Perbaikan:
- Pesan status tersebut sekarang dikirim lewat `bot`, bukan `userbot` --
  `bot` selalu sudah kenal chat itu karena event/perintah masuk dari sana,
  dan pesan status ini memang cuma teks sementara yang di-edit/dihapus,
  tidak perlu berasal dari akun userbot.
- Ditambahkan `await userbot.get_dialogs()` sesaat setelah `userbot.start()`
  di `main.py`, untuk memaksa Telethon menyinkronkan & menyimpan cache
  entity semua grup yang sudah diikuti userbot -- mencegah error serupa
  saat userbot join Voice Chat.

## 10. Persiapan deploy ke VPS Linux & source sharing
- `database/db.py`: anotasi tipe `X | None` (butuh Python 3.10+) diganti
  jadi `Optional[X]` (kompatibel Python 3.9 ke atas) -- beberapa distro
  Linux masih ship Python 3.9 secara default.
- File baru: `setup_vps.sh` (instalasi otomatis ffmpeg, Deno, venv, &
  dependensi Python di VPS Ubuntu/Debian/CentOS), `musicbot.service`
  (template systemd supaya bot auto-restart & auto-start saat boot),
  `.gitignore` (agar `.env`, sesi, database, dan `downloads/` tidak ikut
  ter-share saat push ke Git), dan `README.md` (panduan lengkap setup &
  deploy). Sudah diverifikasi tidak ada kode yang bergantung pada
  path/OS tertentu (tidak ada backslash hardcode, tidak ada `os.system`,
  semua path relatif) -- codebase ini sudah portable Linux/Windows/macOS.

---

**Tidak ada perintah/perilaku yang dihapus** — semua fitur (play, queue, film,
VIP, admin panel, ban, dsb.) tetap berjalan sama seperti sebelumnya dari sisi
pengguna. Perubahan murni di "dapur"-nya: lebih hemat CPU, RAM, disk, dan
panggilan API.
