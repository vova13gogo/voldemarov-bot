import os

TOKEN = os.getenv("TOKEN", "7373333768:AAHCHwMLBypQxRpb3pfntIOaVvYT3v13raM")
DATABASE_URL = os.getenv("DATABASE_URL", "")  # Railway подставит автоматически

MIN_WORDS = 3
GENERATE_LENGTH = 20
DEFAULT_REPLY_CHANCE = 15
