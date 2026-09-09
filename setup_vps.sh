#!/usr/bin/env bash
# ================================================================
# setup_vps.sh — Skrip setup otomatis MusicBot untuk VPS Linux
# Mendukung distro berbasis Debian/Ubuntu (apt) dan RHEL/CentOS/
# AlmaLinux/Rocky (dnf/yum). Jalankan dari dalam folder project:
#
#   chmod +x setup_vps.sh
#   ./setup_vps.sh
# ================================================================
set -e

echo "=============================================="
echo " MusicBot — Setup Otomatis VPS Linux"
echo "=============================================="

# --- 1. Deteksi package manager ---
if command -v apt-get >/dev/null 2>&1; then
    PKG_INSTALL="sudo apt-get update -y && sudo apt-get install -y"
    DEPS="python3 python3-venv python3-pip ffmpeg unzip curl git"
elif command -v dnf >/dev/null 2>&1; then
    PKG_INSTALL="sudo dnf install -y"
    DEPS="python3 python3-pip ffmpeg unzip curl git"
elif command -v yum >/dev/null 2>&1; then
    PKG_INSTALL="sudo yum install -y"
    DEPS="python3 python3-pip ffmpeg unzip curl git"
else
    echo "❌ Package manager tidak dikenali (bukan apt/dnf/yum)."
    echo "   Silakan install manual: python3, python3-venv, pip, ffmpeg, curl, git"
    exit 1
fi

echo "📦 Menginstall dependensi sistem (python3, ffmpeg, dll)..."
eval "$PKG_INSTALL $DEPS"

# --- 2. Install Deno (runtime JS untuk yt-dlp / ekstraksi YouTube) ---
if ! command -v deno >/dev/null 2>&1; then
    echo "📦 Menginstall Deno (dibutuhkan yt-dlp untuk ekstraksi YouTube)..."
    curl -fsSL https://deno.land/install.sh | sh
    export PATH="$HOME/.deno/bin:$PATH"
    if ! grep -q '.deno/bin' "$HOME/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.deno/bin:$PATH"' >> "$HOME/.bashrc"
    fi
    # Symlink ke /usr/local/bin supaya terbaca juga oleh proses systemd
    # (service systemd TIDAK membaca ~/.bashrc, jadi kalau hanya
    # ditambahkan ke PATH shell saja, yt-dlp yang dijalankan lewat
    # `systemctl start musicbot` tetap tidak akan menemukan Deno).
    if [ -f "$HOME/.deno/bin/deno" ]; then
        sudo ln -sf "$HOME/.deno/bin/deno" /usr/local/bin/deno
    fi
    echo "✅ Deno terpasang di \$HOME/.deno/bin (dan di-symlink ke /usr/local/bin/deno)"
else
    echo "✅ Deno sudah terpasang: $(deno --version | head -n1)"
fi

# --- 3. Virtual environment Python ---
echo "🐍 Membuat virtual environment Python (venv/)..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Menginstall dependensi Python dari requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# --- 4. Siapkan file .env ---
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 File .env dibuat dari .env.example -- WAJIB diisi sebelum menjalankan bot!"
else
    echo "ℹ️  File .env sudah ada, tidak ditimpa."
fi

mkdir -p downloads

echo ""
echo "=============================================="
echo "✅ Setup selesai!"
echo "=============================================="
echo "Langkah selanjutnya:"
echo "  1. Edit file .env dan isi semua kredensial (nano .env)"
echo "  2. Aktifkan venv:      source venv/bin/activate"
echo "  3. Jalankan bot:       python3 main.py"
echo ""
echo "Untuk menjalankan otomatis di background (auto-restart & auto-start"
echo "saat VPS reboot), lihat instruksi systemd di README.md."
echo "=============================================="
