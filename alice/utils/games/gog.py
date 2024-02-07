import httpx
import re
from alice import GAME_CHAT
from bs4 import BeautifulSoup
from pyrofork import utils
from pyrofork.types import InlineKeyboardButton, InlineKeyboardMarkup

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"

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

async def get_game_description(requests: httpx.AsyncClient, game_url: str) -> str:
	request = await requests.get(game_url, headers={"User-Agent": UA}, timeout=30)
	soup = await utils.run_sync(BeautifulSoup, request.text, "html.parser")
	desc = await utils.run_sync(soup.select_one, ".description")
	return await utils.run_sync(desc.find, "b")

async def get_free_gog_games(client):
	requests = httpx.AsyncClient(http2=True)
	db = client.db['freegames']
	request = await requests.get("https://www.gog.com/", headers={"User-Agent": UA}, timeout=30)
	soup = await utils.run_sync(BeautifulSoup, request.text, "html.parser")
	giveaway = await utils.run_sync(soup.find, "a", {"id": "giveaway"})

	if giveaway is None:
		return

	# Game name
	banner_title = await utils.run_sync(giveaway.find, "span", class_="giveaway-banner__title")
	game_name = get_game_name(banner_title.text)
	all_games = (await db.find_one({'name': 'gog'}))['game_name']
	if game_name in all_games:
		return

	# Game URL
	ng_href = giveaway.attrs["ng-href"]
	game_url = f"https://www.gog.com{ng_href}"

	# Game image
	image_url_class = await utils.run_sync(giveaway.find, "source", attrs={"srcset": True})
	image_url = image_url_class.attrs["srcset"].strip().split()
	image_url = f"https:{image_url[0]}"
	
	# Game description
	desc = await get_game_description(requests, game_url)

	text = f"<b>🎮 {game_name}</b>"
	text += f"\n💲 Price: <strike>-</strike> <b>$0.0</b>"
	text += f"\n\nℹ️ {desc}"
	text += f"\n\n#gog #giveaway"
	button = InlineKeyboardMarkup(
		[
			[InlineKeyboardButton(text=f"Claim", url=game_url)]
		]
	)
	await client.send_photo(chat_id=GAME_CHAT, photo=image_url, caption=text, reply_markup=button)
	await db.update_one({'name': 'gog'},{"$push": {'game_name': game_name}})
	await requests.aclose()
