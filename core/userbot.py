from telethon import TelegramClient
from telethon.sessions import StringSession
import config

userbot = TelegramClient(StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH)
