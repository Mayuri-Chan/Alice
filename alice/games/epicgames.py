import datetime
import os
import pytz
from alice import GAME_CHAT, TZ
from alice.db import epicgames as sql
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict

import requests

# Epic's backend API URL for the free games promotion
EPIC_API: str = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

# HTTP params for the US free games
PARAMS: Dict[str, str] = {
	"locale": "en-US",
	"country": "US",
	"allowCountries": "US",
}

async def get_free_epic_games(client):
	response = requests.get(EPIC_API, params=PARAMS)

	# Find the free games in the response
	for game in response.json()["data"]["Catalog"]["searchStore"]["elements"]:
		game_name = game["title"]
		game_id = game["id"]
		check = sql.check_epic(game_id)
		if check:
			continue
		final_price = game["price"]["totalPrice"]["originalPrice"] - game["price"]["totalPrice"]["discount"]
		if int(final_price) == 0:
			original_price = (game["price"]["totalPrice"]["fmtPrice"]["originalPrice"])
			for image in game["keyImages"]:
				if image["type"] == "OfferImageWide":
					banner = image["url"]
					break
			if not game["promotions"]:
				continue
			for promotion in game["promotions"]["promotionalOffers"]:
				for offer in promotion["promotionalOffers"]:
					end_date = pytz.timezone(TZ).localize(datetime.datetime.strptime(offer["endDate"], "%Y-%m-%dT%H:%M:%S.%fZ"))
					exp = end_date.strftime("%d %b, %Y - %I:%M %p %Z")
					break
				break
			desc = game["description"]
			if game["offerType"] == "BASE_GAME":
				offer_type = "Base Games"
				hastag = "#freegames #games"
			elif game["offerType"] == "DLC":
				offer_type = game["offerType"]
				hastag = "#freedlc #dlc"
			else:
				offer_type = game["offerType"]
				hastag = ""
			url = "https://store.epicgames.com/"
			if product_slug := game["productSlug"]:
				game_url = f"https://www.epicgames.com/en-US/p/{product_slug}"
			else:
				for offer in game["offerMappings"]:
					if offer["pageSlug"]:
						page_slug = offer["pageSlug"]
						game_url = f"https://www.epicgames.com/en-US/p/{page_slug}"
						break
			text = f"<b>🎮 {game_name}</b>"
			text += f"\n💲 Price: <strike>{original_price}</strike> <b>$0.0</b>"
			text += f"\n⌛️ Exp: {exp}"
			text += f"\n🧩 Type: {offer_type}"
			text += f"\n\nℹ️ {desc}"
			text += f"\n\n{hastag} #epicgames #giveaway"
			button = InlineKeyboardMarkup(
				[
					[InlineKeyboardButton(text=f"Claim", url=game_url)]
				]
			)
			#result = {
			#	'text': text,
			#	'button': button
			#}
			#yield result
			if banner:
				await client.send_photo(chat_id=GAME_CHAT, photo=banner, caption=text, reply_markup=button)
			else:
				await client.send_message(chat_id=GAME_CHAT, text=text, reply_markup=button)
			sql.add(game_id)
