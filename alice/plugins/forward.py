import os

from alice.db import setting as sql
from alice.alice import Alice
from alice.utils.string import build_keyboard, parse_button
from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardMarkup

@Alice.on_message(filters.group & filters.command("settopics"))
async def set_topics(c,m):
	chat_id = m.chat.id
	if not m.chat.is_forum:
		return await m.reply_text("This group is not a forum!")
	thread_id = m.message_thread_id
	if not m.forward_from_chat:
		return await m.reply_text("Please send /settopics to Update channel then forward it here!")
	channel_id = m.forward_from_chat.id
	sql.add(channel_id,chat_id,thread_id)
	await m.reply_text("Channel Connected")

async def forward_m(c,m):
	button = None
	channel_id = m.chat.id
	check = sql.check_channel(channel_id)
	if check:
		chat_id = check.chat_id
		thread_id = check.thread_id
		caption = ""
		button = None
		text = None
		caption = None
		if m.text:
			with open('temp2.txt', 'w') as f:
				f.write(m.text.html)
			file = open('temp2.txt', 'r')
			text = file.read()
			text, button = parse_button(text)
			if button:
				button = build_keyboard(button)
				button = InlineKeyboardMarkup(button)
			elif m.reply_markup:
				button = m.reply_markup
			else:
				button = None
			if os.path.isfile(os.path.join(os.getcwd(), 'temp2.txt')):
				os.remove(os.path.join(os.getcwd(), 'temp2.txt'))
			return await c.send_message(chat_id, text, reply_to_message_id=thread_id, reply_markup=button, parse_mode=enums.ParseMode.HTML)
		if m.caption:
			with open('temp2.txt', 'w') as f:
				f.write(m.caption.html)
			file = open('temp2.txt', 'r')
			caption = file.read()
			caption, button = parse_button(caption)
		if button:
			button = build_keyboard(button)
			button = InlineKeyboardMarkup(button)
		elif m.reply_markup:
			button = m.reply_markup
		else:
			button = None
		file = await m.download()
		if m.photo:
			await c.send_photo(chat_id=chat_id, photo=file, caption=caption, reply_to_message_id=thread_id, reply_markup=button, parse_mode=enums.ParseMode.HTML)
		elif m.document:
			await c.send_document(chat_id=chat_id, document=file, caption=caption, reply_to_message_id=thread_id, reply_markup=button, parse_mode=enums.ParseMode.HTML)
		elif m.video:
			await c.send_video(chat_id=chat_id, video=file, caption=caption, reply_to_message_id=thread_id, reply_markup=button, parse_mode=enums.ParseMode.HTML)
		elif m.animation:
			await c.send_animation(chat_id=chat_id, animation=file, caption=caption, reply_to_message_id=thread_id, reply_markup=button, parse_mode=enums.ParseMode.HTML)
		elif m.audio:
			await c.send_audio(chat_id=chat_id, audio=file, caption=caption, reply_to_message_id=thread_id, reply_markup=button, parse_mode=enums.ParseMode.HTML)
		elif m.sticker:
			await c.send_sticker(chat_id=chat_id, sticker=m.sticker.file_id, reply_to_message_id=thread_id)
		if os.path.isfile(os.path.join(os.getcwd(), 'temp2.txt')):
			os.remove(os.path.join(os.getcwd(), 'temp2.txt'))
