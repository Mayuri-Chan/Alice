from alice import API_ID, API_HASH, BOT_SESSION, WORKERS, init_help
from alice.plugins import list_all_plugins
from pyrogram import Client

class Alice(Client):
	def __init__(self):
		name = self.__class__.__name__.lower()
		super().__init__(
			name,
			session_string=BOT_SESSION,
			api_id=API_ID,
			api_hash= API_HASH,
			workers=WORKERS,
			plugins=dict(
				root=f"{name}.plugins"
			),
			sleep_threshold=180
		)

	async def start(self):
		await super().start()
		await init_help(list_all_plugins())
		print("---[Alice Services is Running...]---")

	async def stop(self, *args):
		await super().stop()
		print("---[Bye]---")
		print("---[Thankyou for using my bot...]---")
