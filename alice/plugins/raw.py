from alice.alice import Alice
from pyrogram import raw

@Alice.on_raw_update()
async def _raw(c,u,_,__):
	db = c.db['bot_settings']
	state = await db.find_one({'name': 'state'})
	value = state['value']
	pts = value["pts"]
	date = value["date"]
	qts = value["qts"]
	new_pts = None
	new_date = None
	new_qts = None
	if hasattr(u, "pts"):
		new_pts = u.pts
	if hasattr(u, "date"):
		new_date = u.date
	if hasattr(u, "qts"):
		new_qts = u.qts
	if not new_pts and not new_date and not new_qts:
		return
	value = {'pts': new_pts or pts, 'qts': new_qts or qts, 'date': new_date or date}
	await db.update_one({'name': 'state'}, {"$set": {'value': value}})
