import threading

from alice import BASE, SESSION
from sqlalchemy import Column, UnicodeText

class Gog(BASE):
	__tablename__ = "gog_list"
	game_id = Column(UnicodeText, primary_key=True)

	def __init__(self,game_id):
		self.game_id = game_id


	def __repr__(self):
		return "<Gog for %s>" % (self.game_id)


Gog.__table__.create(checkfirst=True)
GOG_INSERTION_LOCK = threading.RLock()

def add(game_id):
	with GOG_INSERTION_LOCK:
		prev = SESSION.query(Gog).get(game_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		gog_filt = Gog(game_id)
		SESSION.merge(gog_filt)
		SESSION.commit()

def check_gog(game_id):
	with GOG_INSERTION_LOCK:
		find = SESSION.query(Gog).get(game_id)
		if find:
			return True
		return False
