import os
from bson import json_util
from datetime import datetime
from mayuri import DATABASE_URL, SESSION_NAME, BACKUP_CHAT
from async_pymongo import AsyncClient

async def backup(client):
	db = AsyncClient(DATABASE_URL)
	bot_db = db["alice"]
	datas = {}
	for col in await bot_db.list_collection_names():
		datas[col] = []
		async for data in bot_db[col].find():
			datas[col].append(data)
	datas = json_util.dumps(datas2, indent = 4)
	now = datetime.now()
	now_formatted = now.strftime("%Y%m%d-%H:%M:%S")
	filename = f"{os.getcwd()}/backup-alice-{now_formatted}.json"
	with open(filename, 'w') as f:
		f.write(datas)
		f.close()
	await client.send_document(chat_id=BACKUP_CHAT, document=filename)
	os.remove(filename)

	session_db = db[SESSION_NAME]
	datas2 = {}
	for col in await session_db.list_collection_names():
		datas2[col] = []
		async for data in session_db[col].find():
			datas2[col].append(data)
	datas2 = json_util.dumps(datas2, indent = 4)
	filename2 = f"{os.getcwd()}/backup-sessions-alice-{now_formatted}.json"
	with open(filename2, 'w') as f:
		f.write(datas2)
		f.close()
	await client.send_document(chat_id=BACKUP_CHAT, document=filename2)
	os.remove(filename2)
