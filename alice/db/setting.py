import threading

from alice import BASE, SESSION
from sqlalchemy import Column, BigInteger, Boolean, UnicodeText

class Settings(BASE):
	__tablename__ = "settings"
	channel_id = Column(BigInteger, primary_key=True)
	chat_id = Column(BigInteger)
	thread_id = Column(BigInteger)

	def __init__(self,channel_id,chat_id,thread_id):
		self.channel_id = channel_id
		self.chat_id = chat_id
		self.thread_id = thread_id

	def __repr__(self):
		return "<Settings for %s>" % (self.channel_id)


Settings.__table__.create(checkfirst=True)
SETTINGS_INSERTION_LOCK = threading.RLock()

def add(channel_id,chat_id,thread_id):
	with SETTINGS_INSERTION_LOCK:
		prev = SESSION.query(Settings).get(channel_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		welcome_filt = Settings(channel_id,chat_id,thread_id)
		SESSION.merge(welcome_filt)
		SESSION.commit()

def check_channel(channel_id):
	with SETTINGS_INSERTION_LOCK:
		find = SESSION.query(Settings).get(channel_id)
		if find:
			return find
		return False
