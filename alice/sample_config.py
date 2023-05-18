class Config(object):
	API_ID = "" # from my.telegram.org
	API_HASH = "" # from my.telegram.org
	BOT_TOKEN = "" # bot token from https://t.me/BotFather
	DATABASE_URL = "mongodb://user:pass@localhost:port"
	SESSION_NAME = "alice_sessions"
	AUTO_BACKUP = True
	BACKUP_CHAT = -1001234
	PREFIX = ['/','$']
	WORKERS = 6
	GAME_CHAT = -1001234
