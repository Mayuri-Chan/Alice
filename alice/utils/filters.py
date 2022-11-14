import asyncio

from alice import PREFIX
from pyrogram import enums, filters
from pyrogram.errors import FloodWait

async def admin_check(_, c, m):
	if m.sender_chat:
		try:
			curr_chat = await c.get_chat(m.chat.id)
		except FloodWait as e:
			asyncio.sleep(e.value)
		if m.sender_chat.id == m.chat.id: # Anonymous admin
			return True
		if curr_chat.linked_chat:
			if (
				m.sender_chat.id == curr_chat.linked_chat.id and
				not m.forward_from
			): # Linked channel owner
				return True
		return False
	chat_id = m.chat.id
	user_id = m.from_user.id
	try:
		all_admin = await c.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
	except FloodWait as e:
		asyncio.sleep(e.value)
	admin_list = []
	async for admin in all_admin:
		admin_list.append(admin.id)
	if user_id in admin_list:
		return True
	return False

admin_only = filters.create(admin_check)
