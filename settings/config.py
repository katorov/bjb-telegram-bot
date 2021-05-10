import os
from pathlib import Path

from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(str(BASE_DIR / '.env'))

DEBUG = env.bool("DEBUG", default=True)

BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")
PGUSER = env.str("TELEGRAM_DB_USER")
PGPASSWORD = env.str("TELEGRAM_DB_PASSWORD")
IP = env.str("TELEGRAM_DB_HOST")
DATABASE = env.str("TELEGRAM_DB_NAME")
BASE_AMOUNT = env.int("BASE_AMOUNT")

POSTGRES_URI = f"postgresql://{PGUSER}:{PGPASSWORD}@{IP}/{DATABASE}"

ADMINS = env.list("TELEGRAM_ADMINS")

QIWI_TOKEN = os.getenv("QIWI_TOKEN")
QIWI_WALLET = os.getenv("QIWI_WALLET")
QIWI_PUBKEY = os.getenv("QIWI_PUBKEY")
