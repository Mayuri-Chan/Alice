import os
from dateutil import tz
from dateutil.parser import parse as parse_time
from alice import GAME_CHAT
from alice.db import epicgames as sql
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from typing import Dict

import requests

# Epic's backend API URL for the free games promotion
EPIC_API: str = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

# HTTP params for the US free games
PARAMS: Dict[str, str] = {
	"locale": "id-ID",
	"country": "ID",
	"allowCountries": "ID",
}

async def get_free_epic_games(client):
	response = requests.get(EPIC_API, params=PARAMS)

	imgs = []
	datas = []
	offer_types = []
	exps = None
	diff = False
	# Find the free games in the response
	i = 1
	# Find the free games in the response
	for game in response.json()["data"]["Catalog"]["searchStore"]["elements"]:
		game_name = game["title"]
		game_id = game["id"]
		check = sql.check_epic(game_id)
		if check:
			continue
		final_price = game["price"]["totalPrice"]["originalPrice"] - game["price"]["totalPrice"]["discount"]
		if int(final_price) == 0:
			if len(game["promotions"]["promotionalOffers"]) == 0:
				continue
			original_price = (game["price"]["totalPrice"]["fmtPrice"]["originalPrice"])
			for image in game["keyImages"]:
				if image["type"] == "OfferImageWide":
					banner = image["url"]
					break
			if banner:
				imgs.append(banner)
			if not game["promotions"]:
				continue
			for promotion in game["promotions"]["promotionalOffers"]:
				for offer in promotion["promotionalOffers"]:
					if not exps:
						exps = offer["endDate"]
					elif exps and exps != offer["endDate"]:
						diff = True
						continue
					break
				break
			desc = game["description"]
			if game["offerType"] not in offer_types:
				offer_types.append(game["offerType"])
			if game["offerType"] == "BASE_GAME":
				offer_type = "Base Games"
			elif game["offerType"] == "DLC":
				offer_type = game["offerType"]
			else:
				offer_type = game["offerType"]
			url = "https://store.epicgames.com/"
			if product_slug := game["productSlug"]:
				game_url = f"https://www.epicgames.com/en-US/p/{product_slug}"
			else:
				for offer in game["offerMappings"]:
					if offer["pageSlug"]:
						page_slug = offer["pageSlug"]
						game_url = f"https://www.epicgames.com/en-US/p/{page_slug}"
						break
			datas.append({'game_name': game_name, 'original_price': original_price, 'offer_type': offer_type, 'desc': desc, 'game_url': game_url})
			sql.add(game_id)
		i = i+1

	if len(datas) == 0:
		return
	end_date = parse_time(exps).astimezone(tz.tzlocal())
	exp = end_date.strftime("%d %b, %Y - %I:%M %p %Z")
	if len(datas) == 1:
		text = f"<b>🎮 {datas[0]['game_name']}</b>"
		if game["price"]["totalPrice"]["originalPrice"] == game["price"]["totalPrice"]["discount"]:
			price = datas[0]['original_price']
		else:
			price = f"<strike>{datas[0]['original_price']}</strike> <b>Rp 0,0</b>"
		text += f"\n💲 Price: {price}"
		text += f"\n⌛️ Exp: {exp}"
		text += f"\n🧩 Type: {datas[0]['offer_type']}"
		text += f"\n\nℹ️ {datas[0]['desc']}"
		if datas[0]['offer_type'] == "DLC":
			hastag = "#freedlc #dlc"
		elif datas[0]['offer_type'] == "Base Games":
			hastag = "#freegames #games"
		else:
			hastag = ""
		text += f"\n\n{hastag} #epicgames #giveaway"
		button = InlineKeyboardMarkup(
			[
				[InlineKeyboardButton(text=f"Claim", url=datas[0]['game_url'])]
			]
		)
		if len(imgs) > 0:
			await client.send_photo(chat_id=GAME_CHAT, photo=imgs[0], caption=text, reply_markup=button)
		else:
			await client.send_message(chat_id=GAME_CHAT, text=text, reply_markup=button)
	else:
		text = f"<b>🎮 Free Games</b>"
		text += f"\n⌛️ Exp: {exp}\n"
		btn = []
		i = 1
		for data in datas:
			text += f"\n{i}. <b><a href='{data['game_url']}'>{data['game_name']}</a></b>"
			if {data['offer_type']} == "DLC":
				text += " (DLC)"
			if game["price"]["totalPrice"]["originalPrice"] == game["price"]["totalPrice"]["discount"]:
				text += f" {data['original_price']}"
			else:
				text += f" <strike>{data['original_price']}</strike> <b>Rp 0,00</b>\n"
			i = i+1
		hastag = ""
		if "BASE_GAME" in offer_types:
			hastag += " #freegames #games"
		if "DLC" in offer_types:
			hastag += " #freedlc #dlc"
		text += f"\n\n{hastag} #epicgames #giveaway"
		if len(imgs) == 0:
			await client.send_message(chat_id=GAME_CHAT, text=text, reply_markup=button)
		elif len(imgs) == 1:
			await client.send_photo(chat_id=GAME_CHAT, photo=imgs[0], caption=text, reply_markup=button)
		else:
			media = []
			count = len(imgs)
			i = 1
			for img in imgs:
				if i == count:
					media.append(InputMediaPhoto(media=img,caption=text))
				else:
					media.append(InputMediaPhoto(media=img))
				i = i+1
			await client.send_media_group(chat_id=GAME_CHAT, media=media)
	if diff:
		return await get_free_epic_games(client)
