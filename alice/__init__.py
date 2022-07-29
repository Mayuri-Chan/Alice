import os

from pyrogram import Client

from alice.config import Config
API_ID = Config.API_ID
API_HASH = Config.API_HASH
BOT_SESSION = Config.BOT_SESSION

client = Client(
	BOT_SESSION,
	api_id=API_ID,
	api_hash=API_HASH
)
