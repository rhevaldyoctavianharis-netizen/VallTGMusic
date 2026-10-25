<div align="right">
  <strong>🇬🇧 English</strong> | <a href="README-id.md">🇮🇩 Indonesia</a>
</div>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7F00FF,100:E100FF&height=220&section=header&text=VallTgMusic%20New&fontSize=58&fontColor=ffffff&fontAlignY=38&desc=Telegram%20Voice%20Chat%20Music%20Bot%20%E2%80%A2%20Fast%20%E2%80%A2%20Efficient%20%E2%80%A2%20Ready%20to%20Deploy&descAlignY=60&descSize=18" alt="VallTgMusic New" width="100%"/>

<a href="https://github.com/rhevaldyoctavianharis-netizen/VallTGMusic">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=20&pause=1200&color=C77DFF&center=true&vCenter=true&width=620&lines=Music+%26+video+streaming+in+Voice+Chat;Resource+efficient%2C+portable+on+all+OS;Auto-restart+with+systemd;Deploy+to+Heroku+in+1+click" alt="Typing SVG" />
</a>

<br/>

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-Bot%20%2B%20Userbot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![PyTgCalls](https://img.shields.io/badge/PyTgCalls-Voice%20Chat-7F00FF?style=for-the-badge)
![yt-dlp](https://img.shields.io/badge/yt--dlp-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)

<br/>

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rhevaldyoctavianharis-netizen/VallTGMusic)
<a href="https://t.me/OneDotOneBot"><img src="https://img.shields.io/badge/%F0%9F%8E%A7%20Try%20Bot-@OneDotOneBot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Try Bot @OneDotOneBot" height="28"/></a>

<br/>

[✨ Features](#-features) •
[🤖 Try Bot](#-try-bot) •
[📋 Requirements](#-requirements) •
[🚀 Deploy Heroku](#-deploy-to-heroku) •
[🖥️ VPS Setup](#️-quick-vps-linux-setup) •
[🔁 Auto-Start](#-auto-start--auto-restart-systemd) •
[🧯 Troubleshooting](#-troubleshooting) •
[🤝 Contact](#-collaboration--contact) •
[👤 Credits](#-credits)

</div>

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### 🎧 Voice Chat
Stream music directly to group **Voice Chats** via PyTgCalls, with an auto-joining userbot account.

</td>
<td width="33%" valign="top">

### ⚡ Resource Efficient
Optimized to be lightweight on CPU, RAM, and disk storage, making it run smoothly on small VPS instances.

</td>
<td width="33%" valign="top">

### 🌍 Portable
Runs seamlessly on **Linux, Windows, and macOS**. An automated setup script is available for VPS.

</td>
</tr>
<tr>
<td width="33%" valign="top">

### ▶️ Stable YouTube
Extraction using **yt-dlp** with a JavaScript runtime (**Deno** or **Node.js**) to effectively bypass bot-checks.

</td>
<td width="33%" valign="top">

### 🔁 Always On
Included **systemd** templates keep the bot running on VPS reboot and auto-restarts it upon crash.

</td>
<td width="33%" valign="top">

### ☁️ Ready to Deploy
**Deploy to Heroku** button with a configured variables form, plus ready-to-use `Procfile` and `app.json`.

</td>
</tr>
</table>

Additional options via `.env`: **`FSUB_CHANNEL`** (force subscribe channel) and **`CREDIT_CHANNEL`** (your credit channel).

---

## 🤖 Try Bot

Want to see how it works before deploying it yourself? Try our demo bot:

<div align="center">

<a href="https://t.me/OneDotOneBot"><img src="https://img.shields.io/badge/Open%20in%20Telegram-@OneDotOneBot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Open @OneDotOneBot"/></a>

</div>

---

## 📋 Requirements

| Component | Description |
|---|---|
| 🐍 **Python** | **3.9 or newer** (3.10+ recommended) |
| 🎞️ **ffmpeg** | Installed on the system |
| 🦕 **Deno** or **Node.js 20+** | Required by `yt-dlp` for stable YouTube extraction |
| 👤 **Userbot Account** | A personal Telegram account (not a bot) that will join the Voice Chat |
| 🤖 **Telegram Bot** | Created via [@BotFather](https://t.me/BotFather) |

---

## ⚙️ `.env` Configuration

Copy the example file to `.env`, then fill in the values:

```bash
# Linux / macOS
cp .env.example .env

# Windows (CMD)
copy .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Open `.env` with your favorite editor (`nano .env` on Linux/macOS, or Notepad on Windows). All variables are explained in `.env.example`. In short:

| Variable | Required | Source |
|---|:---:|---|
| `API_ID`, `API_HASH` | ✅ | [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | ✅ | [@BotFather](https://t.me/BotFather) |
| `SESSION_STRING` | ✅ | Telethon StringSession (instructions in `.env.example`) |
| `ADMIN_ID` | ✅ | Your own Telegram ID (check via [@userinfobot](https://t.me/userinfobot)) |
| `CREDIT_CHANNEL` | ➖ | Your channel link |
| `FSUB_CHANNEL` | ➖ | Force-subscribe channel username |

### 🔑 Get `SESSION_STRING`

Easiest way: generate a string session using the following bot.

<div align="center">

<a href="https://t.me/ssgenduabot"><img src="https://img.shields.io/badge/Generate%20String%20Session-@ssgenduabot-7F00FF?style=for-the-badge&logo=telegram&logoColor=white" alt="Generate String Session @ssgenduabot"/></a>

</div>

1. Open [@ssgenduabot](https://t.me/ssgenduabot) and follow the instructions.
2. Copy the given string session to `SESSION_STRING` in your `.env`.

Alternative without a bot: generate it yourself using Telethon `StringSession` (instructions in `.env.example`).

> 🔒 **Important:** `SESSION_STRING` grants full access to a Telegram account, treat it like a password. It is highly recommended to use a **spare userbot account**, not your main account, and never share your `SESSION_STRING` or `BOT_TOKEN`.

---

## 🚀 Deploy to Heroku

> Heroku does not use the `.env` file. All settings are read from **Config Vars**, and the Deploy button will display a form.

**1.** Prepare your `SESSION_STRING` first, either via [@ssgenduabot](https://t.me/ssgenduabot) or locally on your computer (not on Heroku).

**2.** Click the button below, then fill out the form:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rhevaldyoctavianharis-netizen/VallTGMusic)

| Variable | Required | Description |
|---|:---:|---|
| `API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `SESSION_STRING` | ✅ | Telethon StringSession for the userbot |
| `ADMIN_ID` | ✅ | Your Telegram ID (owner) |
| `CREDIT_CHANNEL` | ➖ | Example: `https://t.me/yourchannel` |
| `FSUB_CHANNEL` | ➖ | Force subscribe `@channel` (empty = disabled) |

Other variables can be modified in **Settings → Config Vars** after deployment.

<details>
<summary><b>⌨️ Deploy via Heroku CLI</b></summary>

```bash
heroku create your-app-name
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
<summary><b>⚠️ Important Heroku Limitations</b></summary>

- **Ephemeral Storage.** Databases, session files, and the `downloads/` folder are wiped when the dyno restarts (approx. every 24 hours). For persistent data, use external storage.
- **`localhost` cannot be used.** External services require a public address.
- **No browser cookies.** The server lacks a browser, use `YT_COOKIES_FILE` if necessary.
- **Do not commit secrets.** `.env`, `SESSION_STRING`, and API keys should never be pushed to a public repository.

</details>

---

## 🖥️ Quick VPS Linux Setup

Applies to Ubuntu, Debian, CentOS, and similar distributions.

```bash
# 1. Upload/clone source to VPS, then enter the directory
cd VallTGMusic

# 2. Run the automated setup script (installs ffmpeg, Deno, venv, dependencies)
chmod +x setup_vps.sh
./setup_vps.sh

# 3. Copy the configuration example, then fill in credentials
cp .env.example .env
nano .env

# 4. Run the bot (test manually first)
source venv/bin/activate
python3 main.py
```

If the terminal displays `🚀 MusicBot Professional Berhasil Berjalan!` without errors, press `Ctrl+C` and proceed to the **Auto-Start** section to keep the bot running in the background.

---

## 🔁 Auto-Start & Auto-Restart (systemd)

The bot will automatically start when the VPS reboots and restart itself if it crashes, eliminating the need to log in via SSH every time.

```bash
# 1. Copy & adjust the service template
sudo cp musicbot.service /etc/systemd/system/musicbot.service
sudo nano /etc/systemd/system/musicbot.service
#    → adjust "User", "WorkingDirectory", and "ExecStart"
#      with your project folder location & VPS user

# 2. Enable & start
sudo systemctl daemon-reload
sudo systemctl enable musicbot      # auto-start on boot
sudo systemctl start musicbot       # start now

# 3. Check status & logs
sudo systemctl status musicbot
tail -f /var/log/musicbot.log       # real-time logs
```

| Command | Function |
|---|---|
| `sudo systemctl restart musicbot` | Manual restart |
| `sudo systemctl stop musicbot` | Stop the bot |
| `sudo systemctl status musicbot` | View status |

---

## 🧯 Troubleshooting

<details>
<summary><b>Warning <code>No supported JavaScript runtime could be found</code> from yt-dlp</b></summary>

Install **Deno** (automatically installed by `setup_vps.sh`) or Node.js 20+. If the warning persists:

- Run `deno --version` to ensure Deno is recognized in the PATH of the session running the bot.
- If using systemd, ensure `ExecStart` in `musicbot.service` uses python from `venv/bin/python3` (not system python), and the service PATH includes the `deno` location.

</details>

<details>
<summary><b>Error <code>ValueError: Could not find the input entity</code> from userbot</b></summary>

Ensure the userbot account has explicitly joined the group where the bot is being used as a **member**.

</details>

<details>
<summary><b>Bot is running but cannot join Voice Chat</b></summary>

Make sure the **userbot** account (not the bot account) has joined the group as a regular member, and the group has an **active Voice Chat** running.

</details>

---

## 📤 Sharing Source Code Safely

```bash
git init
git add .
git commit -m "Initial commit"
```

A `.gitignore` is already provided so that `.env`, session files, databases, and the `downloads/` folder **are not committed**. Anyone cloning the repo only needs to repeat the setup steps with their own `.env`.

> ⚠️ If pushing the repo to a **public** GitHub, never commit a filled `.env`. Run `git status` before the first commit to ensure `.env` is not tracked.

---

## 🤝 Collaboration & Contact

Need collaboration, support, or something else? Visit my portfolio website:

<div align="center">

<a href="https://rhevaldy.my.id"><img src="https://img.shields.io/badge/Portfolio-rhevaldy.my.id-E100FF?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Portfolio rhevaldy.my.id"/></a>
<a href="https://t.me/rapaldy"><img src="https://img.shields.io/badge/Telegram-@rapaldy-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram @rapaldy"/></a>

</div>

---

## 👤 Credits

<div align="center">

| | |
|---|---|
| 👨‍💻 **Developer** | [@rapaldy](https://t.me/rapaldy) |
| 📢 **Channel** | [@youlittleboy](https://t.me/youlittleboy) |

<a href="https://t.me/rapaldy"><img src="https://img.shields.io/badge/Chat%20Developer-@rapaldy-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram @rapaldy"/></a>
<a href="https://t.me/youlittleboy"><img src="https://img.shields.io/badge/Join%20Channel-@youlittleboy-7F00FF?style=for-the-badge&logo=telegram&logoColor=white" alt="Channel @youlittleboy"/></a>

</div>

Feel free to use or modify this project, but please **retain the credits** above. Thank you! 🙏

---

<div align="center">

### 💜 Created by [@rapaldy](https://t.me/rapaldy) • Channel [@youlittleboy](https://t.me/youlittleboy)

**⭐ Leave a star if you find this project useful!**

<br/>

![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![Made in Indonesia](https://img.shields.io/badge/Made%20in-Indonesia-red?style=flat-square)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:E100FF,100:7F00FF&height=100&section=footer" width="100%" alt=""/>

</div>