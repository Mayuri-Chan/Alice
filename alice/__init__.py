from importlib import import_module

ENV = os.environ.get("ENV", False)
if ENV:
	API_ID = os.environ.get("API_ID", None)
	API_HASH = os.environ.get("API_HASH", None)
	BOT_SESSION = os.environ.get("BOT_SESSION", None)
	WORKERS = int(os.environ.get("WORKERS", 6))
else:
	from alice.config import Config
	config = Config()
	API_ID = config.API_ID
	API_HASH = config.API_HASH
	BOT_SESSION = config.BOT_SESSION
	WORKERS = config.WORKERS

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
