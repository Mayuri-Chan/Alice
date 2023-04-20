import threading

from alice import BASE, SESSION
from sqlalchemy import Column, UnicodeText

class BotSettings(BASE):
	__tablename__ = "bot_settings"
	name = Column(UnicodeText, primary_key=True)
	value = Column(UnicodeText)

	def __init__(self,name,value):
		self.name = name
		self.value = value

	def __repr__(self):
		return "<BotSettings for %s>" % (self.user_id)

BotSettings.__table__.create(checkfirst=True)
SETTINGS_INSERTION_LOCK = threading.RLock()

def update_settings(name,value):
	with SETTINGS_INSERTION_LOCK:
		prev = SESSION.query(BotSettings).get(name)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		settings_filt = BotSettings(name,value)
		SESSION.merge(settings_filt)
		SESSION.commit()

def get_settings(name):
	with SETTINGS_INSERTION_LOCK:
		return SESSION.query(BotSettings).get(name)
