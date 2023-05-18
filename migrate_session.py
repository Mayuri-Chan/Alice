import aiosqlite
import asyncio
import pymongo

mongodb_uri = "mongodb://127.0.0.1"
mongodb_dbname = "my_sessions"
sqlite_file_path = "/path/to/my_bot.session"

async def main():
	print(f"Importing sessions from {sqlite_file_path} to {mongodb_dbname} database...")
	db = pymongo.MongoClient(mongodb_uri)[mongodb_dbname]
	conn = await aiosqlite.connect(sqlite_file_path)
	cur = await conn.cursor()
	await cur.execute("select * from sessions")
	cols = list(map(lambda x: x[0], cur.description))
	rows = await cur.fetchall()
	count = 0
	for row in rows:
		data = {}
		data["_id"] = count
		i = 0
		for col in cols:
			data[col] = row[i]
			i = i+1
		db.session.insert_one(data)
		count = count+1

	await cur.execute("select * from peers")
	cols = list(map(lambda x: x[0], cur.description))
	rows = await cur.fetchall()
	for row in rows:
		data = {}
		i = 0
		for col in cols:
			if col == "id":
				col = "_id"
			data[col] = row[i]
			i = i+1
		db.peers.insert_one(data)
	print("Done")
	await conn.close()

asyncio.run(main())
