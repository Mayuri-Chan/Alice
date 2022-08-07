import os

from alice.alice import Alice
from alice.utils.string import build_keyboard, parse_button
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup

@Alice.on_message(filters.channel, group=100)
async def channel_watcher(c,m):
	chat_id = m.chat.id
	if m.reply_markup:
		return
	if m.text:
		with open('temp.txt', 'w') as f:
			f.write(m.text)
		file = open('temp.txt', 'r')
		msg = file.read()
		text, button = parse_button(msg)
		button = build_keyboard(button)
		if not button:
			return os.remove(os.path.join(os.getcwd(), 'temp.txt'))
		button = InlineKeyboardMarkup(button)
		if m.forward_from:
			await m.delete()
			await c.send_message(chat_id=chat_id, text=text, reply_markup=button)
			return os.remove(os.path.join(os.getcwd(), 'temp.txt'))
		await m.edit(text=text, reply_markup=button)
		os.remove(os.path.join(os.getcwd(), 'temp.txt'))

	elif m.caption: # m.photo or m.video or m.animation:
		with open('temp.txt', 'w') as f:
			f.write(m.caption)
		file = open('temp.txt', 'r')
		msg = file.read()
		text, button = parse_button(msg)
		button = build_keyboard(button)
		if not button:
			return os.remove(os.path.join(os.getcwd(), 'temp.txt'))
		button = InlineKeyboardMarkup(button)
		if m.forward_from:
			if m.photo:
				await c.send_photo(chat_id=chat_id, photo=m.photo.file_id, caption=text, reply_markup=button)
			elif m.video:
				await c.send_video(chat_id=chat_id, video=m.video.file_id, caption=text, reply_markup=button)
			elif m.animation:
				await c.send_animation(chat_id=chat_id, animation=m.animation.file_id, caption=text, reply_markup=button)
			await m.delete()
			return os.remove(os.path.join(os.getcwd(), 'temp.txt'))
		await m.edit_caption(caption=text, reply_markup=button)
		os.remove(os.path.join(os.getcwd(), 'temp.txt'))

@Alice.on_message(filters.private & filters.command("preview"))
async def preview(c,m):
	if not m.reply_to_message:
		return
	if m.reply_to_message.text:
		text = m.reply_to_message.text
		with open('temp.txt', 'w') as f:
			f.write(text)
		file = open('temp.txt', 'r')
		msg = file.read()
		text, button = parse_button(msg)
		button = build_keyboard(button)
		if not button:
			await m.reply_text("No button found!")
			return #os.remove(os.path.join(os.getcwd(), 'temp.txt'))
		button = InlineKeyboardMarkup(button)
		await m.reply_text(text=text, reply_markup=button)
		#os.remove(os.path.join(os.getcwd(), 'temp.txt'))
	elif m.reply_to_message.caption:
		caption = m.reply_to_message.caption
		with open('temp.txt', 'w') as f:
			f.write(caption)
		file = open('temp.txt', 'r')
		msg = file.read()
		text, button = parse_button(msg)
		button = build_keyboard(button)
		if not button:
			await m.reply_text("No button found!")
			return os.remove(os.path.join(os.getcwd(), 'temp.txt'))
		button = InlineKeyboardMarkup(button)
		if m.photo:
			await m.reply_photo(photo=m.photo.file_id, caption=text, reply_markup=button)
		elif m.video:
			await m.reply_video(video=m.video.file_id, caption=text, reply_markup=button)
		elif m.animation:
			await m.reply_animation(animation=m.animation.file_id, caption=text, reply_markup=button)
		os.remove(os.path.join(os.getcwd(), 'temp.txt'))
