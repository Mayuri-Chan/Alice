class Config(object):
	API_ID = "" # from my.telegram.org
	API_HASH = "" # from my.telegram.org
	BOT_SESSION = "" # bot token from https://t.me/BotFather
	DATABASE_URL = "postgresql://user:pass@localhost:port/db"
	PREFIX = ['/','$']
	WORKERS = 6
	GAME_CHAT = "-1001234"
	TZ = "Asia/Jakarta"