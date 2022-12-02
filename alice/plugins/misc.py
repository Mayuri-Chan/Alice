from alice.alice import Alice
from pyrogram import filters

@Alice.on_message(filters.private & filters.command("start"))
async def preview(c,m):
	text = "Hello!\nuse /help for usage."
	await m.reply_text(text=text)

@Alice.on_message(filters.private & filters.command("help"))
async def help(c,m):
	text = """
To use this bot just add the bot as Admin to your channel.
then when you post something use markdown below for creating button:
> `[Button](btn:https://example.com)`

if you want to make 2 button in one line just add `:same` after link on 2nd button
also the next button if you want to make more than 2 button in same line.
example:
> `[Button 1 line 1](btn:https://example1.com)
  [Button 1 line 2](btn:https://example2.com)
  [Button 2 line 2](btn:https://example3.com:same)
  [Button 1 line 3](btn:https://example4.com)
  [Button 2 line 3](btn:https://example5.com:same)
  [Button 3 line 3](btn:https://example6.com:same)`

if you want to preview before posting your message just send the message here and then reply with `/preview`

For channel forwarder. Your group must be a forum (Topics enabled).
1. send `/settopics` to your channel
2. forward the `/settopics` message from your channel to your desired topics in your group.
	"""
	await m.reply_text(text=text)
