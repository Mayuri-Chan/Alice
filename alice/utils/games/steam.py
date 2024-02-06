import httpx
import re
import os
from pathlib import Path

from alice import GAME_CHAT
from bs4 import BeautifulSoup
from pyrofork import utils
from pyrofork.types import InlineKeyboardButton, InlineKeyboardMarkup

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
STEAM_URL = "https://store.steampowered.com/search/?maxprice=free&specials=1"

async def get_free_steam_games(client):
	requests = httpx.AsyncClient(http2=True)
	db = client.db['freegames']
	request = await requests.get(STEAM_URL, headers={"User-Agent": UA}, timeout=30)
	soup = await utils.run_sync(BeautifulSoup, request.text, "html.parser")

	games = await utils.run_sync(soup.find_all, "a", class_="search_result_row")
	for game in games:
		game_name: str = get_game_name(game)
		all_games = (await db.find_one({'name': 'steam'}))['game_name']
		if game_name in all_games:
			continue
		game_url: str = get_game_url(game)
		image_url: str = get_game_image(game)
		request2 = await requests.get(game_url, headers={"User-Agent": UA}, timeout=30)
		soup2 = await utils.run_sync(BeautifulSoup, request2.text, "html.parser")
		original_price = (await utils.run_sync(soup2.select_one, ".discount_original_price")).get_text()
		discount_price = (await utils.run_sync(soup2.select_one, ".discount_final_price")).get_text()
		text = await utils.run_sync(soup2.find_all, 'div',{'class': "game_area_description"})
		desc = 'No description available'
		for t in text:
			f = re.search(r'(About This)(\s){0,}(Game|Content)(\s){0,}([A-Za-z0-9\.\!\?\n].*\n.*)', t.get_text('\n'))
			if f:
				desc = f.group(5)
		text = (await utils.run_sync(soup2.select_one, ".game_purchase_discount_quantity")).get_text()
		exp = re.search(r'(before\s)([A-Za-z0-9\@\:\s]{0,})', text).group(2)
		text = (await utils.run_sync(soup2.select_one, ".game_area_purchase")).get_text()
		if re.search("Downloadable Content", text):
			offer_type = "DLC"
			hastag = "#freedlc #dlc"
		else:
			offer_type = "Base Game"
			hastag = "#freegames #games"
		text = f"<b>🎮 {game_name}</b>"
		text += f"\n💲 Price: <strike>{original_price}</strike> <b>{discount_price}</b>"
		text += f"\n⌛️ Exp: {exp}"
		text += f"\n🧩 Type: {offer_type}"
		text += f"\n\nℹ️ {desc}"
		text += f"\n\n{hastag} #steam #giveaway"
		button = InlineKeyboardMarkup(
			[
				[InlineKeyboardButton(text=f"Claim", url=game_url)]
			]
		)
		await client.send_photo(chat_id=GAME_CHAT, photo=image_url, caption=text, reply_markup=button)
		await db.update_one({'name': 'steam'},{"$push": {'game_name': game_name}})
		await requests.aclose()

def get_game_image(game):
	"""
	Get the game ID and create image URL.
	Args:
		game: Contains information about the game.
	Returns:
		Image url for the game.
	"""
	game_id = game["data-ds-appid"]
	image_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game_id}/header.jpg"
	return image_url


def get_game_url(game):
	"""
	Get the game url.
	Args:
		game: Contains information about the game.
	Returns:
		Game URL.
	"""
	game_url = game["href"]
	return game_url


def get_game_name(game):
	"""
	Get the game name.
	Args:
		game: Contains information about the game.
	Returns:
		The game name.
	"""
	game_name_class = game.find("span", class_="title")
	game_name = game_name_class.text
	return game_name
