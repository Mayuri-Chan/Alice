import ast
from alice import API_ID, API_HASH, BOT_SESSION, WORKERS, init_help
from alice.db import bot_settings as sql
from alice.plugins import list_all_plugins
from pyrogram import Client, raw

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
		await self.catch_up()
		await init_help(list_all_plugins())
		print("---[Alice Services is Running...]---")

	async def stop(self, *args):
		state = await self.invoke(raw.functions.updates.GetState())
		value = {"pts": state.pts, "qts": state.qts, "date": state.date}
		sql.update_settings("state", str(value))
		await super().stop()
		print("---[Bye]---")
		print("---[Thankyou for using my bot...]---")

	async def catch_up(self):
		print("---[Recovering gaps...]---")
		while(True):
			state = sql.get_settings("state")
			if not state:
				return
			value = ast.literal_eval(state.value)
			diff = await self.invoke(
					raw.functions.updates.GetDifference(
						pts=int(value["pts"]),
						date=int(value["date"]),
						qts=-1
					)
				)
			if isinstance(diff, raw.types.updates.DifferenceEmpty):
				new_value = {"pts": value["pts"], "qts": value["qts"], "date": diff.date}
				sql.update_settings("state", str(new_value))
				break
			elif isinstance(diff, raw.types.updates.DifferenceTooLong):
				new_value = {"pts": diff.pts, "qts": value["qts"], "date": value["date"]}
				sql.update_settings("state", str(new_value))
				continue
			users = {u.id: u for u in diff.users}
			chats = {c.id: c for c in diff.chats}
			for msg in diff.new_messages:
				self.dispatcher.updates_queue.put_nowait((
					raw.types.UpdateNewMessage(
						message=msg,
						pts=diff.state.pts,
						pts_count=-1
					),
					users,
					chats
				))

			for update in diff.other_updates:
				self.dispatcher.updates_queue.put_nowait((update, users, chats))
			if isinstance(diff, raw.types.updates.Difference):
				break
