import asyncio
from async_pymongo import AsyncClient
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

POSTGRES_URL = "postgresql://user:pass@localhost:port/db"
MONGO_URL = "mongodb://user:pass@localhost:port"

async def migrate():
	BASE = automap_base()
	engine = create_engine(POSTGRES_URL, client_encoding="utf8")
	BASE.prepare(engine, reflect=True)
	SESSION = scoped_session(sessionmaker(bind=engine, autoflush=False))
	tables = BASE.metadata.tables.keys()
	db = AsyncClient(MONGO_URL)['alice']
	epicgames = []
	gog = []
	steam = []
	for table in tables:
		colums = BASE.metadata.tables[table].c.keys()
		for d in eval(f"SESSION.query(BASE.classes.{table}).all()"):
			if table == 'settings':
				item = {}
				for colum in colums:
					item[colum] = eval(f"d.{colum}")
				db.topic_list.insert_one(item)
			if table == 'epic_list':
				epicgames.append(d.game_id)
			if table == 'gog_list':
				gog.append(d.game_id)
			if table == 'steam_list':
				steam.append(d.name)
	await db.freegames.insert_many([
		{'name': 'epicgames', 'game_id': epicgames},
		{'name': 'gog', 'game_name': gog},
		{'name': 'steam', 'game_name': steam}
	])

asyncio.run(migrate())
