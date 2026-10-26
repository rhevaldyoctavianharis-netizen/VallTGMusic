import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
CREDIT_CHANNEL = os.getenv("CREDIT_CHANNEL", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
FSUB_CHANNEL = os.getenv("FSUB_CHANNEL", "")
GITHUB_URL = os.getenv("GITHUB_URL", "https://github.com/rhevaldyoctavianharis-netizen/VallTGMusic")
