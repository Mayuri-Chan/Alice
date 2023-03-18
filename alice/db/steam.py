import threading

from alice import BASE, SESSION
from sqlalchemy import Column, UnicodeText

class Steam(BASE):
	__tablename__ = "steam_list"
	name = Column(UnicodeText, primary_key=True)

	def __init__(self,name):
		self.name = name


	def __repr__(self):
		return "<Steam for %s>" % (self.name)


Steam.__table__.create(checkfirst=True)
STEAM_INSERTION_LOCK = threading.RLock()

def add(name):
	with STEAM_INSERTION_LOCK:
		prev = SESSION.query(Steam).get(name)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		steam_filt = Steam(name)
		SESSION.merge(steam_filt)
		SESSION.commit()

def check_steam(name):
	with STEAM_INSERTION_LOCK:
		find = SESSION.query(Steam).get(name)
		if find:
			return True
		return False
