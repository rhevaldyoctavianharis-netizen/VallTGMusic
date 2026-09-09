from telethon import TelegramClient
import config

bot = TelegramClient('bot_session', config.API_ID, config.API_HASH)
