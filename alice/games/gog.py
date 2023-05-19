import re

import requests
from alice import GAME_CHAT
from bs4 import BeautifulSoup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_game_name(banner_title_text: str) -> str:
	"""
	Get the game name from the banner title.
	Args:
		banner_title_text: The banner title. We will run a regex to get the game name.
	Returns:
		str: The game name, GOG Giveaway if not found.
	"""
	result = re.search(
		r"being with us! Claim (.*?) as a token of our gratitude!",
		banner_title_text,
	)
	if result:
		return result.group(1)
	return "GOG Giveaway"

def get_game_description(game_url: str) -> str:
	request = requests.get(game_url)
	soup = BeautifulSoup(request.text, "html.parser")
	desc = soup.select_one(".description")
	return desc.find("b")

async def get_free_gog_games(client):
	db = client.db['freegames']
	request = requests.get("https://www.gog.com/")
	soup = BeautifulSoup(request.text, "html.parser")
	giveaway = soup.find("a", {"id": "giveaway"})

	# If no giveaway, return an empty list
	if giveaway is None:
		return

	# Game name
	banner_title = giveaway.find("span", class_="giveaway-banner__title")
	game_name = get_game_name(banner_title.text)
	all_games = (await db.find_one({'name': 'gog'}))['game_name']
	if game_name in all_games:
		return

	# Game URL
	ng_href = giveaway.attrs["ng-href"]
	game_url = f"https://www.gog.com{ng_href}"

	# Game image
	image_url_class = giveaway.find("source", attrs={"srcset": True})
	image_url = image_url_class.attrs["srcset"].strip().split()
	image_url = f"https:{image_url[0]}"
	
	# Game description
	desc = get_game_description(game_url)

	if re.search("DLC", game_name):
		offer_type = "DLC"
		hastag = "#freedlc #dlc"
	else:
		offer_type = "Base Game"
		hastag = "#freegames #games"
	text = f"<b>🎮 {game_name}</b>"
	text += f"\n💲 Price: <strike>-</strike> <b>$0.0</b>"
	text += f"\n🧩 Type: {offer_type}"
	text += f"\n\nℹ️ {desc}"
	text += f"\n\n{hastag} #gog #giveaway"
	button = InlineKeyboardMarkup(
		[
			[InlineKeyboardButton(text=f"Claim", url=game_url)]
		]
	)
	await client.send_photo(chat_id=GAME_CHAT, photo=image_url, caption=text, reply_markup=button)
	await db.update_one({'name': 'gog'},{"$push": {'game_name': game_name}})
