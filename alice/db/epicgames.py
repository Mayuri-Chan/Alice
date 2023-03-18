import threading

from alice import BASE, SESSION
from sqlalchemy import Column, UnicodeText

class Epic(BASE):
	__tablename__ = "epic_list"
	game_id = Column(UnicodeText, primary_key=True)

	def __init__(self,game_id):
		self.game_id = game_id


	def __repr__(self):
		return "<Epic for %s>" % (self.game_id)


Epic.__table__.create(checkfirst=True)
EPIC_INSERTION_LOCK = threading.RLock()

def add(game_id):
	with EPIC_INSERTION_LOCK:
		prev = SESSION.query(Epic).get(game_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		epic_filt = Epic(game_id)
		SESSION.merge(epic_filt)
		SESSION.commit()

def check_epic(game_id):
	with EPIC_INSERTION_LOCK:
		find = SESSION.query(Epic).get(game_id)
		if find:
			return True
		return False
