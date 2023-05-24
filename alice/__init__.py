import os
from dotenv import load_dotenv
from importlib import import_module

if os.path.isfile("config.env"):
	load_dotenv("config.env")

API_ID = os.environ.get("API_ID", None)
API_HASH = os.environ.get("API_HASH", None)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
DATABASE_URL = os.environ.get("DATABASE_URL", None)
SESSION_NAME = os.environ.get("SESSION_NAME", None)
AUTO_BACKUP = os.environ.get("AUTO_BACKUP", False)
BACKUP_CHAT = os.environ.get("BACKUP_CHAT", None)
WORKERS = int(os.environ.get("WORKERS", 6))
GAME_CHAT = os.environ.get("GAME_CHAT", None)

BASE = declarative_base()
SESSION = mulaisql()
HELP_COMMANDS = {}

async def init_help(list_all_plugins):
	for plugin in list_all_plugins:
		imported_plugin = import_module("alice.plugins." + plugin)
		if hasattr(imported_plugin, "__PLUGIN__") and imported_plugin.__PLUGIN__:
			if not imported_plugin.__PLUGIN__.lower() in HELP_COMMANDS:
				HELP_COMMANDS[imported_plugin.__PLUGIN__.lower()] = imported_plugin
			else:
				raise Exception("Can't have two plugin with the same name! Please change one")
		if hasattr(imported_plugin, "__HELP__") and imported_plugin.__HELP__:
			HELP_COMMANDS[imported_plugin.__PLUGIN__.lower()] = imported_plugin
