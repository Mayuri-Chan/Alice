from alice import API_ID, API_HASH, AUTO_BACKUP, BOT_TOKEN, SESSION_NAME, WORKERS, init_help
from alice.games.epicgames import get_free_epic_games
from alice.games.gog import get_free_gog_games
from alice.games.steam import get_free_steam_games
from alice.plugins import list_all_plugins
from alice.utils.backup import backup
from apscheduler import RunState
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from async_pymongo import AsyncClient
from pyrogram import Client, raw

class Alice(Client):
	def __init__(self):
		name = self.__class__.__name__.lower()
		conn = AsyncClient(DATABASE_URL)
		super().__init__(
			SESSION_NAME,
			api_id=API_ID,
			api_hash=API_HASH,
			bot_token=BOT_TOKEN,
			mongodb=dict(connection=conn),
			workers=WORKERS,
			plugins=dict(
				root=f"{name}.plugins"
			),
			sleep_threshold=180
		)
		self.db = conn['alice']
		self.scheduler = AsyncScheduler()

	async def start_scheduler(self):
		await self.scheduler.__aenter__()
		if self.scheduler.state == RunState.stopped:
			if AUTO_BACKUP:
				await self.scheduler.add_schedule(self.backup_now, IntervalTrigger(seconds=60*60*6))
			await self.scheduler.add_schedule(self.freegames, IntervalTrigger(seconds=21600))
			await self.scheduler.start_in_background()

	async def freegames(self):
		if 'freegames' not in await self.db.list_collection_names():
			await self.db.freegames.insert(
				{'name': 'epicgames', 'game_id': []},
				{'name': 'gog', 'game_name': []},
				{'name': 'steam', 'game_name': []}
			)
		await get_free_epic_games(self)
		await get_free_gog_games(self)
		await get_free_steam_games(self)

	async def start(self):
		await super().start()
		await self.catch_up()
		await self.start_scheduler()
		await init_help(list_all_plugins())
		print("---[Alice Services is Running...]---")

	async def stop(self, *args):
		db = self.db['bot_settings']
		state = await self.invoke(raw.functions.updates.GetState())
		value = {'pts': state.pts, 'qts': state.qts, 'date': state.date}
		await db.update_one({'name': 'state'}, {"$set": {'value': value}})
		await super().stop()
		print("---[Bye]---")
		print("---[Thankyou for using my bot...]---")

	async def catch_up(self):
		print("---[Recovering gaps...]---")
		while(True):
			db = self.db['bot_settings']
			state = await db.find_one({'name': 'state'})
			if not state:
				state = await self.invoke(raw.functions.updates.GetState())
				value = {'pts': state.pts, 'qts': state.qts, 'date': state.date}
				await db.insert_one({'name': 'state', 'value': value})
				break
			value = state['value']
			diff = await self.invoke(
					raw.functions.updates.GetDifference(
						pts=value['pts'],
						date=value['date'],
						qts=-1
					)
				)
			if isinstance(diff, raw.types.updates.DifferenceEmpty):
				new_value = {'pts': value['pts'], 'qts': value['qts'], 'date': diff.date}
				await db.update_one({'name': 'state'}, {"$set": {'value': value}})
				break
			elif isinstance(diff, raw.types.updates.DifferenceTooLong):
				new_value = {'pts': diff.pts, 'qts': value['qts'], 'date': value['date']}
				await db.update_one({'name': 'state'}, {"$set": {'value': value}})
				continue
			users = {u.id: u for u in diff.users}
			chats = {c.id: c for c in diff.chats}
			if isinstance(diff, raw.types.updates.DifferenceSlice):
				new_state = diff.intermediate_state
			else:
				new_state = diff.state
			for msg in diff.new_messages:
				self.dispatcher.updates_queue.put_nowait((
					raw.types.UpdateNewMessage(
						message=msg,
						pts=new_state.pts,
						pts_count=-1
					),
					users,
					chats
				))

			for update in diff.other_updates:
				self.dispatcher.updates_queue.put_nowait((update, users, chats))
			if isinstance(diff, raw.types.updates.Difference):
				break

	async def backup_now(self):
		await backup(self)
