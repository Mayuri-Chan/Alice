from alice import API_ID, API_HASH, BOT_SESSION, WORKERS, init_help
from alice.games.epicgames import get_free_epic_games
from alice.games.steam import get_free_steam_games
from alice.plugins import list_all_plugins
from apscheduler import RunState
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
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

	async def start_scheduler(self):
		self.scheduler = AsyncScheduler()
		await self.scheduler.__aenter__()
		if self.scheduler.state == RunState.stopped:
			await self.scheduler.add_schedule(self.epicgames, IntervalTrigger(seconds=21600))
			await self.scheduler.add_schedule(self.steam, IntervalTrigger(seconds=21600))
			await self.scheduler.start_in_background()

	async def epicgames(self):
		await get_free_epic_games(self)

	async def steam(self):
		await get_free_steam_games(self)

	async def start(self):
		await super().start()
		await self.start_scheduler()
		await init_help(list_all_plugins())
		print("---[Alice Services is Running...]---")

	async def stop(self, *args):
		await super().stop()
		print("---[Bye]---")
		print("---[Thankyou for using my bot...]---")
