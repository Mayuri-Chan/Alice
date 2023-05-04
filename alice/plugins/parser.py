import os

from alice.alice import Alice
from alice.plugins.forward import forward_m
from alice.utils.string import build_keyboard, parse_button
from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardMarkup

@Alice.on_message(filters.channel, group=1)
async def channel_watcher(c,m):
	db = c.db['topics_list']
	chat_id = m.chat.id
	forward = False
	mess = m
	check = db.find_one({'chat_id': chat_id})
	if check:
		forward = True
	if m.text:
		with open('temp.txt', 'w') as f:
			f.write(m.text.html)
		file = open('temp.txt', 'r')
		msg = file.read()
		text, button = parse_button(msg)
		button = build_keyboard(button)
		if button:
			button = InlineKeyboardMarkup(button)
			if m.forward_from:
				await m.delete()
				mess = await c.send_message(chat_id=chat_id, text=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
			else:
				await m.edit(text=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
	if m.caption: # m.photo or m.video or m.animation:
		with open('temp.txt', 'w') as f:
			f.write(m.caption.html)
		file = open('temp.txt', 'r')
		msg = file.read()
		text, button = parse_button(msg)
		button = build_keyboard(button)
		if button:
			button = InlineKeyboardMarkup(button)
			if m.forward_from:
				if m.photo:
					mess = await c.send_photo(chat_id=chat_id, photo=m.photo.file_id, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
				elif m.video:
					mess = await c.send_video(chat_id=chat_id, video=m.video.file_id, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
				elif m.animation:
					mess = await c.send_animation(chat_id=chat_id, animation=m.animation.file_id, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
				await m.delete()
			else:
				await m.edit_caption(caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
	if forward:
		try:
			await mess.forward(chat_id=check['chat_id'],message_thread_id=check['thread_id'])
		except Exception as e:
			await forward_m(c,mess)
	if os.path.isfile(os.path.join(os.getcwd(), 'temp.txt')):
		os.remove(os.path.join(os.getcwd(), 'temp.txt'))

@Alice.on_message(filters.private & filters.command("preview"))
async def preview(c,m):
	if not m.reply_to_message:
		return
	if m.reply_to_message.text:
		text = m.reply_to_message.text.html
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
		await m.reply_text(text=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
		#os.remove(os.path.join(os.getcwd(), 'temp.txt'))
	elif m.reply_to_message.caption:
		caption = m.reply_to_message.caption.html
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
			await m.reply_photo(photo=m.photo.file_id, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
		elif m.video:
			await m.reply_video(video=m.video.file_id, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
		elif m.animation:
			await m.reply_animation(animation=m.animation.file_id, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=button)
		if os.path.isfile(os.path.join(os.getcwd(), 'temp.txt')):
			os.remove(os.path.join(os.getcwd(), 'temp.txt'))
