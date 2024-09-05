import telebot
from telebot import types, apihelper
from flask import Flask, request, send_file, jsonify, render_template, url_for
from petpetgif.saveGif import save_transparent_gif
from io import BytesIO, StringIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
from pkg_resources import resource_stream
from threading import Thread
import time
import schedule
from curl_cffi import requests, CurlMime
from bs4 import BeautifulSoup
import random
from re import search
import json
import html
import traceback
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio
from sqlalchemy import create_engine
import os
from groq import Groq

time.sleep(3)

username = os.environ['USERNAME']
password = os.environ['PASSWORD']
cursor = create_engine('postgresql://postgres.hdahfrunlvoethhwinnc:gT77Av9pQ8IjleU2@aws-0-eu-central-1.pooler.supabase.com:5432/postgres', pool_recycle=280)

groq_key = os.environ['GROQ_KEY']
neuro = Groq(api_key=groq_key)

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
ses = os.environ['SES']

token = os.environ['BOT_TOKEN']

class ExHandler(telebot.ExceptionHandler):
    def handle(self, exc):
        sio = StringIO(traceback.format_exc())
        sio.name = 'log.txt'
        sio.seek(0)
        bot.send_document(ME_CHATID, sio)
        return True

bot = telebot.TeleBot(token, threaded=True, num_threads=10, parse_mode='HTML', exception_handler = ExHandler())
apihelper.RETRY_ON_ERROR = True

blocked_messages = []
blocked_users = []

'''
nekosas = {
540255407: (16, 4),
7258570440: (17, 2),
523497602: (4, 7),
729883976: (19, 2),
448214297: (29, 4),
503671007: (3, 10),
460507186: (19, 1),
783003689: (27, 1),
5417937009: (11,3)
}
'''
nekosas = [
(16, 4),
(17, 2),
(4, 7),
(19, 2),
(29, 4),
(3, 10),
(19, 1),
(27, 1),
(11,3),
(26,12)
]

SERVICE_CHATID = -1002171923232
NEKOSLAVIA_CHATID = -1001268892138
ME_CHATID = 7258570440
BOT_ID = 6990957141
TIMESTAMP = 3*3600

APP_URL = f'https://nekocringebot.onrender.com/{token}'
app = Flask(__name__)
bot.remove_webhook()
bot.set_webhook(url=APP_URL, allowed_updates=['message', 'callback_query', 'message_reaction', 'message_reaction_count'])

react_id = []

monsters_db = {
"Zero Sugar Monster Energy": "AgACAgIAAyEGAASBdOsgAAILI2bZlfOp1cP2u3jA8J5B6Qf0_QvLAAKX3DEbxZfRSjvK0kfIuRrzAQADAgADeAADNgQ",
"The Original Green Monster Energy": "AgACAgIAAyEGAASBdOsgAAILJGbZlfgH0aTsoWkjbdDjB_N8HdafAAKY3DEbxZfRSgILKPZ8jMj8AQADAgADeAADNgQ",
"Zero Ultra a.k.a. The White Monster": "AgACAgIAAyEGAASBdOsgAAILJWbZlfxxpkxCjfdjYjYkyZTNfRcmAAKa3DEbxZfRSnIEsDuYqON2AQADAgADeAADNgQ",
"Java Monster Salted Caramel": "AgACAgIAAyEGAASBdOsgAAILJmbZlgAB2nigZDWVh8GHt2Xal6d9GwACm9wxG8WX0UprNM5HohMFywEAAwIAA3gAAzYE",
"Juice Monster Mango Loco": "AgACAgIAAyEGAASBdOsgAAILJ2bZlgQdzuTzlmpfwcMPdc29WMsKAAKc3DEbxZfRStna1woedYeQAQADAgADeAADNgQ",
"Rehab Monster Tea & Lemonade": "AgACAgIAAyEGAASBdOsgAAIGMWbYba6rLcEQDUy4uFoN1BfYV2-QAAJ73DEbzCXISl_YOD2I5z6AAQADAgADeAADNgQ",
"Zero-Sugar Ultra Fantasy Ruby Red": "AgACAgIAAyEGAASBdOsgAAIGjmbYbpyEbOrIDsmdreujns32s0AtAAKd3DEbzCXISvDqBd6hFyOGAQADAgADeAADNgQ",
"Java Monster Irish Crème": "AgACAgIAAyEGAASBdOsgAAIH3WbYgHBwsVNjxEjZC2-GzqzAN6xhAAJd3TEbzCXISqpYoVQORjK1AQADAgADeAADNgQ",
"The Original Lo-Carb Monster Energy": "AgACAgIAAyEGAASBdOsgAAIJE2bYiH2--mh5cdtiF8p-mjdjAjuVAAK63TEbzCXISqmRzXgQw6I4AQADAgADeAADNgQ",
"Monster Energy Nitro Super Dry": "AgACAgIAAyEGAASBdOsgAAIHMmbYf49HSyjNhsyyjpFwcLXThxQNAAJB3TEbzCXISgpW0MoQqo0dAQADAgADeAADNgQ",
"Monster Energy Nitro Cosmic Peach": "AgACAgIAAx0ES6HB6gABAffxZtmCCmbE99ypduoQj-B2VecIMp0AAmXjMRsaZslKy9k6MWJVQFoBAAMCAAN4AAM2BA",
"Monster Energy Reserve Peaches n’ Crème": "AgACAgIAAyEGAASBdOsgAAIFvGbYa3pQBBYpPu1Dn7Rdt_ZplwJkAAJE3DEbzCXISpmvF5PLihZjAQADAgADeAADNgQ",
"Monster Energy Reserve Kiwi Strawberry": "AgACAgIAAyEGAASBdOsgAAIGB2bYbW2ELh4RaVJhPvtXeRYEKOIbAAJv3DEbzCXISiK3daX3sIiUAQADAgADeAADNgQ",
"Monster Energy Reserve White Pineapple": "AgACAgIAAyEGAASBdOsgAAIIMWbYgM4GG469GaiwXxvabsSeXAABaAACad0xG8wlyEooqD4SlZeX9gEAAwIAA3gAAzYE",
"Monster Energy Reserve Watermelon": "AgACAgIAAyEGAASBdOsgAAIKEGbYwM5_vk4AAVywZKXeyD722ZEzIwACtd8xG8wlyErWYHPqdcQKpAEAAwIAA3gAAzYE",
"Monster Energy Reserve Orange Dreamsicle": "AgACAgIAAyEGAASBdOsgAAIK5mbZX7qZXXzJHmdybKGN3fKrgQkEAALt3zEbzCXQSq2oSQhO7ScNAQADAgADeAADNgQ",
"Monster Energy Assault": "AgACAgIAAyEGAASBdOsgAAIIc2bYgRvk5YDzfoWhXpKX84rqcxStAAJy3TEbzCXISkVXmdkOb_NnAQADAgADeAADNgQ",
"The Original Monster Energy Super-Premium Import": "AgACAgIAAyEGAASBdOsgAAIKMGbYwl1ZPU7EOMZAZIdTRu8VUO4QAAK_3zEbzCXISlCqw63fqB5DAQADAgADeAADNgQ",
"Zero-Sugar Ultra Peachy Keen": "AgACAgIAAyEGAASBdOsgAAIKimbZWWiIKdoo6HvE6TDM8E2zOqkpAALX3zEbzCXQSjOrXAYId_6LAQADAgADeAADNgQ",
"Zero-Sugar Ultra Watermelon": "AgACAgIAAyEGAASBdOsgAAIF12bYbKp8ss_Yv4LyXLcRR8HRWpNKAAJU3DEbzCXISgtk5JiOQiNZAQADAgADeAADNgQ",
"Zero-Sugar Ultra Gold": "AgACAgIAAx0ES6HB6gABAffDZtlaYu9iMaDUtkxFdG759-4NHuEAApLeMRtJJslKmejDofLS2sIBAAMCAAN4AAM2BA",
"Zero-Sugar Ultra Sunrise": "AgACAgIAAyEGAASBdOsgAAIJQ2bYiMhQpkSHKZ8_F5NMLnXHe8nyAALB3TEbzCXISveqTD5ymUoWAQADAgADeAADNgQ",
"Zero-Sugar Ultra Rosá": "AgACAgIAAyEGAASBdOsgAAILOWbZlkx8WpUbxniS27WqPzEAAcsghwACntwxG8WX0UpvhW8gBleDzAEAAwIAA3gAAzYE",
"Zero-Sugar Ultra Violet a.k.a. The Purple Monster": "AgACAgIAAyEGAASBdOsgAAIGGWbYbYeVBUG9ls5iVgJu_cLYeX4JAAJ13DEbzCXISrhSqgmMg3XkAQADAgADeAADNgQ",
"Zero-Sugar Ultra Red": "AgACAgIAAyEGAASBdOsgAAIJkWbYiTN3uBvkbW_A4lF9DwHqoe_RAALP3TEbzCXISqXejboaOj5_AQADAgADeAADNgQ",
"Zero-Sugar Ultra Blue a.k.a. The Blue Monster": "AgACAgIAAx0ES6HB6gABAfdIZthsjj4oDWEer9wrIOjKtfGof_MAAsDgMRtJJsFKzOm39IlYhGoBAAMCAAN4AAM2BA",
"Zero-Sugar Ultra Black": "AgACAgIAAyEGAASBdOsgAAIKw2bZXdChlsNMKBV95FEfV4U6EV_VAALj3zEbzCXQShCZbdavxoDDAQADAgADeAADNgQ",
"Zero-Sugar Ultra Strawberry Dreams": "AgACAgIAAyEGAASBdOsgAAIKhGbZWWI6QNzyIOmKPbS5feoW0BgzAALW3zEbzCXQSooXrCNC8oqaAQADAgADeAADNgQ",
"Java Monster Mean Bean": "AgACAgIAAyEGAASBdOsgAAIGVWbYbf_baQycucQO9hJym4Y_j-y1AAKM3DEbzCXISgcHfKmKkwFPAQADAgADeAADNgQ",
"Java Monster Loca Moca": "AgACAgIAAyEGAASBdOsgAAIIGWbYgLR0aG2MIjccFMEIpCiDFUXjAAJj3TEbzCXISgM_i2Ci1JvvAQADAgADeAADNgQ",
"Café Latte": "AgACAgIAAyEGAASBdOsgAAII32bYgYfFVRIgulkmUgZVcH2e25qaAAJ-3TEbzCXISgngXIfEFei5AQADAgADeAADNgQ",
"Java Monster Triple Shot French Vanilla": "AgACAgIAAx0ES6HB6gABAffTZtladhJ5LRLrG-Tmyxde86gDQIsAApTeMRtJJslK6_EQRBsAARsiAQADAgADeAADNgQ",
"Java Monster Triple Shot Mocha": "AgACAgIAAyEGAASBdOsgAAILQ2bZlniP6mr0NbNZzI8SuzFyV2s2AAKh3DEbxZfRSuwE_wvC0yD1AQADAgADeAADNgQ",
"Juice Monster Aussie Style Lemonade": "AgACAgIAAyEGAASBdOsgAAIJfGbYiRnVvxrtaXU6-N9XkrNBl34CAALL3TEbzCXISpTyYbSrpWqcAQADAgADeAADNgQ",
"Juice Monster Khaotic": "AgACAgIAAyEGAASBdOsgAAIIjmbYgTVYsiOOjKLxT3aV-oTs_ZdYAAJ23TEbzCXISvV3aIFUbaxlAQADAgADeAADNgQ",
"Juice Monster Pacific Punch": "AgACAgIAAyEGAASBdOsgAAIGOmbYbbm5t2AsGRs9JeXM5WoxyfliAAJ93DEbzCXISuwQCxdOmHhAAQADAgADeAADNgQ",
"Juice Monster Pipeline Punch": "AgACAgIAAyEGAASBdOsgAAIGoGbYbsYi_2iiYDOERzI_MPO2D4zoAAKh3DEbzCXIStnDCBOGt1e7AQADAgADeAADNgQ",
"Juice Monster Rio Punch": "AgACAgIAAyEGAASBdOsgAAIHCGbYcLA00W4zL9X1Yud98K8pwKS-AALW3DEbzCXISr2C2KfhBJG7AQADAgADeAADNgQ",
"Rehab Monster Peach Tea": "AgACAgIAAyEGAASBdOsgAAIFxWbYa4S4fmkJXYz_Dvt5WDjx51n3AAJH3DEbzCXISt_qpz_WnRmwAQADAgADeAADNgQ",
"Rehab Monster Wild Berry": "AgACAgIAAyEGAASBdOsgAAIIambYgQ-GHvFmFTxl2gtMKf4Qh7RtAAJv3TEbzCXISuXQFGuApsnZAQADAgADeAADNgQ",
"Rehab Monster Green Tea": "AgACAgIAAyEGAASBdOsgAAILS2bZlplPq2B5zD16gcuckXdmsctRAAKj3DEbxZfRSqxD7pEy9b8GAQADAgADeAADNgQ",
"Rehab Monster Strawberry Lemonade": "AgACAgIAAyEGAASBdOsgAAIHHWbYe3OOkqadZL_WStGmOzuaIRsYAAIq3TEbzCXISpT0Q9ud10KEAQADAgADeAADNgQ",
"Rehab Monster Watermelon": "AgACAgIAAx0ES6HB6gABAfdFZthseAW_yDLvkl3d9xOB_v7PBtQAAr_gMRtJJsFK_UsyhD1ZGCABAAMCAAN4AAM2BA",
"Das Original Green Monster Energy": "AgACAgIAAyEGAASBdOsgAAIKPmbY5bvWI0u6hi_FysT_fOTB7zFIAAIo4DEbzCXISsU8kUQD0AakAQADAgADeAADNgQ",
"Ultra a.k.a. Das Weiße Monster": "AgACAgIAAx0ES6HB6gABAfgJZtmCPN2nktbwXyhZaS7V0KngaQMAAmrjMRsaZslKJnRC0ZO6ktYBAAMCAAN4AAM2BA",
"Lewis Hamilton Zero Sugar": "AgACAgIAAx0ES6HB6gABAff1ZtmCE2MIhsKeqX-8Rsgnc9NZRJYAAmjjMRsaZslK_IeI9e_GQ8wBAAMCAAN4AAM2BA",
"Zero Zucker Ultra Gold": "AgACAgIAAyEGAASBdOsgAAIGJWbYbZhoepyQPBrUUuhjrDwPwm44AAJ43DEbzCXISg553SBHBzCsAQADAgADeAADNgQ",
"Ultra Fiesta Mango": "AgACAgIAAyEGAASBdOsgAAIK2WbZX0NyDDAB99QZQ_YBu4KxqJOkAALm3zEbzCXQSuwiRRSEo33vAQADAgADeAADNgQ",
"Ultra Paradise": "AgACAgIAAyEGAASBdOsgAAIFuWbYa3g1J9xGstVi7rxV2ARk10x1AAJD3DEbzCXISoOucwksvtBjAQADAgADeAADNgQ",
"Juiced Monster Aussie Lemonade": "AgACAgIAAyEGAASBdOsgAAIHO2bYf5qnZzp_PUkre-tCTvaEVjiSAAJD3TEbzCXISspdK8If6VG7AQADAgADeAADNgQ",
"Zero-Sugar Ultra Fiesta Mango": "AgACAgIAAyEGAASBdOsgAAIG-WbYcICngjGjhx_HH9ZpcRXdLY5kAALT3DEbzCXISmCiUEZmuV-DAQADAgADeAADNgQ",
"Super Dry": "AgACAgIAAyEGAASBdOsgAAIHembYf-M_zZ-iKE5GzZGquX-sh6dDAAJO3TEbzCXISn3y50I9JeEQAQADAgADeAADNgQ",
"Zero-Sugar Ultra Paradise": "AgACAgIAAyEGAASBdOsgAAIFuWbYa3g1J9xGstVi7rxV2ARk10x1AAJD3DEbzCXISoOucwksvtBjAQADAgADeAADNgQ",
"Zero-Sugar Peachy Keen": "AgACAgIAAyEGAASBdOsgAAIHoWbYgBWJ9tVyLZQbI36oZiEAAfO77AACVd0xG8wlyEqVC1U65SvxmwEAAwIAA3gAAzYE",
"Originalni zeleni Monster Energy": "AgACAgIAAyEGAASBdOsgAAIG6GbYcExn37ATShhB7-zI_XANrP8dAALQ3DEbzCXISsN11F_px9uiAQADAgADeAADNgQ",
"VR46 aka. The Doctor Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
"Ultra a.k.a. The White Monster": "AgACAgIAAx0ES6HB6gABAfftZtmB_IccPIAKGHTb-Om_zQx5pqsAAmPjMRsaZslKReo5XKp9OK4BAAMCAAN4AAM2BA",
"Monster Monarch": "AgACAgIAAyEGAASBdOsgAAIJ6WbYwI7yR944kcQvZVwWT0rMqZwRAAKx3zEbzCXISubi8UmSqTaUAQADAgADeAADNgQ",
"Juiced Monster Mixxd Punch": "AgACAgIAAyEGAASBdOsgAAIGiGbYbpFdEowtWhk7wpb6HEOkQrBlAAKb3DEbzCXISnMmAgg26PqUAQADAgADeAADNgQ",
"L'originale : la Monster Energy verte": "AgACAgIAAyEGAASBdOsgAAIJOmbYiLxuVKho_YWPleaYPyX1lvq9AALA3TEbzCXISipdrHcOlTTeAQADAgADeAADNgQ",
"ULTRA FIESTA": "AgACAgIAAyEGAASBdOsgAAIKbGbZWU561u3jYmudItvfqPPbyl15AALV3zEbzCXQSpaYcICVgirKAQADAgADeAADNgQ",
"Juiced Aussie Lemonade": "AgACAgIAAyEGAASBdOsgAAIGXmbYbglVjp-RB9TBIpFIPso8M079AAKP3DEbzCXISn78tv68lfTSAQADAgADeAADNgQ",
"L'Originale Monster Energy avec zéro sucre": "AgACAgIAAyEGAASBdOsgAAIGRmbYbcnZRDL8IQwwS4YtwJM76hu6AAKA3DEbzCXISsu7mXvsA5MsAQADAgADeAADNgQ",
"Peachy Keen": "AgACAgIAAyEGAASBdOsgAAIF8mbYbVD8VQgy8F3qdBrRVN1QeQmsAAJm3DEbzCXISujAiKphZHxfAQADAgADeAADNgQ",
"Bad Apple": "AgACAgIAAyEGAASBdOsgAAIHLGbYf4i2_HL0HxCO156nBXag6svrAAJA3TEbzCXIStAgeSpjTtj9AQADAgADeAADNgQ",
"Оригиналният Зелен Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Juiced Monster Monarch": "AgACAgIAAyEGAASBdOsgAAIJ6WbYwI7yR944kcQvZVwWT0rMqZwRAAKx3zEbzCXISubi8UmSqTaUAQADAgADeAADNgQ",
"Оригиналният Absolutely Zero Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGfGbYbkg9420d4BC_Rkv-19XUff-RAAKY3DEbzCXISlt_xGA7g8PNAQADAgADeAADNgQ",
"Juiced Monster Khaotic": "AgACAgIAAyEGAASBdOsgAAII8WbYgZpL0UQFW44YW6KfTCD3ei3cAAJ_3TEbzCXISpSdAAF3PCtgawEAAwIAA3gAAzYE",
"The Original Lo-Cal Monster Energy": "AgACAgIAAyEGAASBdOsgAAIJW2bYiOdpxtkWvJTT75edsWHDdfwjAALF3TEbzCXISjjMaI8Hx2PYAQADAgADeAADNgQ",
"MONSTER ENERGY RES": "AgACAgIAAyEGAASBdOsgAAIFv2bYa35c7TeqnXysPvGL6wlgEteAAAJF3DEbzCXISkCOIszz3QdyAQADAgADeAADNgQ",
"Zero-Sugar Ultra Fiesta": "AgACAgIAAyEGAASBdOsgAAIF5mbYbTN49PKwWk5U0yqdh-m0GXHaAAJj3DEbzCXIShs4Ty1IeKWlAQADAgADeAADNgQ",
"Punch Monster Papillon": "AgACAgIAAyEGAASBdOsgAAILbGbZlx_VLjddVo3idetKhWZE61MyAAKq3DEbxZfRSvjNG9Q6Zc0KAQADAgADeAADNgQ",
"Rehab Monster Wild Berry Tea": "AgACAgIAAyEGAASBdOsgAAILbWbZlyRXC1GQS21GhUYtwraF_gZvAAKr3DEbxZfRSrpOHpXWL6SrAQADAgADeAADNgQ",
"Monster Rehab Iced Tea & Lemonade": "AgACAgIAAyEGAASBdOsgAAIKO2bY5bhINEqrKWJ5YvIGGajzK7MKAAIn4DEbzCXISlkqpJfNj8qgAQADAgADeAADNgQ",
"Juiced Monster Pipeline Punch": "AgACAgIAAx0ES6HB6gABAfd_ZtkvAAFjbjKqagGI5jArYk4oO9UeAALp3TEbSSbJSqweIbckQKUfAQADAgADeAADNgQ",
"Juiced Monster Μixxd Punch": "AgACAgIAAyEGAASBdOsgAAIGiGbYbpFdEowtWhk7wpb6HEOkQrBlAAKb3DEbzCXISnMmAgg26PqUAQADAgADeAADNgQ",
"Juiced Monarch": "AgACAgIAAyEGAASBdOsgAAIHrWbYgCOtWxLdPAbb37dNEBXxcQrqAAJW3TEbzCXISnY1QcYDHYEUAQADAgADeAADNgQ",
"Originální zelený Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Ultra Rosá bez cukru": "AgACAgIAAyEGAASBdOsgAAIHTWbYf68geenD6IpGK__a6oAKqvaqAAJG3TEbzCXISuda3JFdGw6uAQADAgADeAADNgQ",
"Ultra a.k.a. bílý Monster": "AgACAgIAAyEGAASBdOsgAAIF6WbYbTdxAbYV_2x8WRFGDBV71eCpAAJk3DEbzCXISsvcqSd7X6GgAQADAgADeAADNgQ",
"Absolutely Zero Monster Energy": "AgACAgIAAyEGAASBdOsgAAIHj2bYgAAB-l8IFxeXFGoHIEUkWg5iuQACUt0xG8wlyEqCQq1_LXpaCwEAAwIAA3gAAzYE",
"Ultra Fiesta bez cukru": "AgACAgIAAyEGAASBdOsgAAIKbGbZWU561u3jYmudItvfqPPbyl15AALV3zEbzCXQSpaYcICVgirKAQADAgADeAADNgQ",
"Ultra Paradise bez cukru": "AgACAgIAAyEGAASBdOsgAAIFuWbYa3g1J9xGstVi7rxV2ARk10x1AAJD3DEbzCXISoOucwksvtBjAQADAgADeAADNgQ",
"Ultra Watermelon bez cukru": "AgACAgIAAyEGAASBdOsgAAIF12bYbKp8ss_Yv4LyXLcRR8HRWpNKAAJU3DEbzCXISgtk5JiOQiNZAQADAgADeAADNgQ",
"Ultra Golden Pineapple bez cukru   ": "AgACAgIAAyEGAASBdOsgAAIF9WbYbVOQ_wequyFW7Kf233CMv8fYAAJo3DEbzCXISgwxsMITLv11AQADAgADeAADNgQ",
"Juiced Monster Bad Apple": "AgACAgIAAx0ES6HB6gABAffvZtmCBinDQlK8CEHmcae4HFw-km8AAmTjMRsaZslK79pOSR7gseMBAAMCAAN4AAM2BA",
"Zero Zucker Ultra Peachy Keen": "AgACAgIAAyEGAASBdOsgAAIHjGbYf_1y-jwqbzu-w2FYKhmNbFC9AAJR3TEbzCXIStgRsdxXVJyKAQADAgADeAADNgQ",
"Das Original Zero Zucker Monster Energy": "AgACAgIAAyEGAASBdOsgAAIHj2bYgAAB-l8IFxeXFGoHIEUkWg5iuQACUt0xG8wlyEqCQq1_LXpaCwEAAwIAA3gAAzYE",
"Monster Reserve Orange Dreamsicle": "AgACAgIAAyEGAASBdOsgAAIG0WbYbwi5iaCh-e6OUu3-xVypiG3xAAKt3DEbzCXISmj_PbjXmC4aAQADAgADeAADNgQ",
"VR46 alias Der Doctor Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
"Zero Zucker Ultra Rosá": "AgACAgIAAyEGAASBdOsgAAIH4GbYgHUEvuZKQ-y5BCGZ-Q9VP9tWAAJe3TEbzCXISiock3GpjzTzAQADAgADeAADNgQ",
"Zero Zucker Ultra Fiesta": "AgACAgIAAyEGAASBdOsgAAIIgmbYgSr2ejBLki1rQGuoASAYXDs-AAJz3TEbzCXISuYnkx3bUoU0AQADAgADeAADNgQ",
"Zero Zucker Ultra Paradise": "AgACAgIAAyEGAASBdOsgAAIHy2bYgFo9j48u_8-yi55zzL4-ycKDAAJa3TEbzCXISkTODigON5H3AQADAgADeAADNgQ",
"Zero Zucker Ultra Watermelon": "AgACAgIAAyEGAASBdOsgAAILgmbZl31TP3C4c0hLoCqpJTjECTvEAAKv3DEbxZfRStPcQKoNlQEeAQADAgADeAADNgQ",
"Monster Rehab Peach Iced Tea": "AgACAgIAAyEGAASBdOsgAAIF1GbYbG5IPnhMmU5UDYu0LyMI7PW5AAJS3DEbzCXISnFeNP__pw2fAQADAgADeAADNgQ",
"Den originale - Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Ultra White": "AgACAgIAAyEGAASBdOsgAAIF6WbYbTdxAbYV_2x8WRFGDBV71eCpAAJk3DEbzCXISsvcqSd7X6GgAQADAgADeAADNgQ",
"Juiced Bad Apple": "AgACAgIAAyEGAASBdOsgAAIIQGbYgN-I9pWKXxrMP4V74CqDijq6AAJs3TEbzCXISu_mbg586sNXAQADAgADeAADNgQ",
"Roheline Originaal Monster Energy": "AgACAgIAAyEGAASBdOsgAAIIcGbYgRjoxexwHhygw8epQXCcFWCjAAJx3TEbzCXISr1fupNnZG2_AQADAgADeAADNgQ",
"Ultra ehk Valge Monster": "AgACAgIAAyEGAASBdOsgAAIF6WbYbTdxAbYV_2x8WRFGDBV71eCpAAJk3DEbzCXISsvcqSd7X6GgAQADAgADeAADNgQ",
"Suhkruvaba Ultra Paradise": "AgACAgIAAyEGAASBdOsgAAIFuWbYa3g1J9xGstVi7rxV2ARk10x1AAJD3DEbzCXISoOucwksvtBjAQADAgADeAADNgQ",
"Suhkruvaba Ultra Watermelon": "AgACAgIAAyEGAASBdOsgAAIF12bYbKp8ss_Yv4LyXLcRR8HRWpNKAAJU3DEbzCXISgtk5JiOQiNZAQADAgADeAADNgQ",
"Juiced Monster Mango Loco": "AgACAgIAAyEGAASBdOsgAAIGbWbYbjahNjHo97JxRt2HFHP0OzF3AAKV3DEbzCXISjYAAaN0BuPgSgEAAwIAA3gAAzYE",
"VR46 ehk The Doctor Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
"LH44 Monster Energy": "AgACAgIAAyEGAASBdOsgAAILIWbZYTYRsCkIJcNv1aT9rCsVfglxAAL23zEbzCXQSjChLri5nFs-AQADAgADeAADNgQ",
"Suhkruvaba Ultra Fiesta": "AgACAgIAAx0ES6HB6gABAfexZtlaTgHSbfrXcybGhMuYtTMXFicAAo_eMRtJJslKXp6GWTZYy0ABAAMCAAN4AAM2BA",
"Suhkruvaba Ultra Violet ehk Lilla Monster": "AgACAgIAAyEGAASBdOsgAAIIDWbYgKghJyLJrcLleMDZasgjfiGaAAJi3TEbzCXISmdX6c-gu-QNAQADAgADeAADNgQ",
"Suhkruvaba Ultra Golden Pineapple": "AgACAgIAAyEGAASBdOsgAAIK8WbZX93JddZlQJe717M_z9l1x5HgAALv3zEbzCXQStkc-ucevv2HAQADAgADeAADNgQ",
"Suhkruvaba Ultra Rosá": "AgACAgIAAyEGAASBdOsgAAIHZWbYf8pCxOqhnO_E-xyv--EKjCJ9AAJK3TEbzCXISotByecKAZ-SAQADAgADeAADNgQ",
"Juiced Monster Pacific Punch": "AgACAgIAAyEGAASBdOsgAAIF0WbYbGpuTsTHbo5h6VJ7HtMI-bjmAAJQ3DEbzCXISjGpNUElLaM8AQADAgADeAADNgQ",
"Zero Ultra White": "AgACAgIAAyEGAASBdOsgAAIGdmbYbkLIRJM61MAT-cdsTXvonV54AAKX3DEbzCXISgP7eMFrUHVSAQADAgADeAADNgQ",
"Zero Ultra Fiesta Mango": "AgACAgIAAyEGAASBdOsgAAIGxGbYbve_qf0CO86f-cNhID8lJ0K_AAKq3DEbzCXISpzzoDwi4ky4AQADAgADeAADNgQ",
"Zero Ultra Gold": "AgACAgIAAyEGAASBdOsgAAIIJWbYgL_JYnr8jiVnb0rEMxuyjphvAAJn3TEbzCXISqshz4wOM0d5AQADAgADeAADNgQ",
"Monster Mule": "AgACAgIAAyEGAASBdOsgAAIGDWbYbXhaafO7_PLjewpuxgd7tQojAAJx3DEbzCXISrWDvOOiIfAkAQADAgADeAADNgQ",
"Monster Reserve Watermelon": "AgACAgIAAyEGAASBdOsgAAIKJ2bYwlPuiZCqePDfMTeUEjjVQ3gUAAK93zEbzCXISpKQ8H_-epvDAQADAgADeAADNgQ",
"Zero Ultra Paradise": "AgACAgIAAyEGAASBdOsgAAIHPmbYf5xG3ayACfGpb8MlhIZuAzlOAAJE3TEbzCXISmO8_pN5e3GeAQADAgADeAADNgQ",
"Zero Ultra Watermelon": "AgACAgIAAyEGAASBdOsgAAIGEGbYbXujNegzya9d9JD5gnQJv-_3AAJy3DEbzCXISg6qUoCEP3iSAQADAgADeAADNgQ",
"Zero Ultra Red": "AgACAgIAAyEGAASBdOsgAAIGK2bYbae6Me6JK_qRYE67sL7e5KYUAAJ63DEbzCXIStHQj8b8puL1AQADAgADeAADNgQ",
"Monster Ultra Rosá": "AgACAgIAAyEGAASBdOsgAAIGYWbYbg3MwU1n5-xOSN0nUoybMDL_AAKS3DEbzCXISipZAodnXQ23AQADAgADeAADNgQ",
"Monster Ultra Peachy Keen ": "AgACAgIAAyEGAASBdOsgAAIGWGbYbgIS4aR1nW4TLqbcIekOmKF4AAKN3DEbzCXISlkbtxkaBaEiAQADAgADeAADNgQ",
"Juiced Monster Ripper": "AgACAgIAAyEGAASBdOsgAAILnWbZl-y26YGYj6vlrxb8th0bbRKYAAKx3DEbxZfRSnHM5K7T17gbAQADAgADeAADNgQ",
"Monster Juiced Bad Apple": "AgACAgIAAyEGAASBdOsgAAIF3WbYbLGQjvGjetz3q1e7OCDJiw1NAAJW3DEbzCXISjOona5d1m5eAQADAgADeAADNgQ",
"Juiced Monster Mixxd": "AgACAgIAAyEGAASBdOsgAAIF_mbYbWKEFBwZMFItBG4vXZF9ze_XAAJr3DEbzCXIStoHQkEgGGnYAQADAgADeAADNgQ",
"Originalni Zero Sugar Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGRmbYbcnZRDL8IQwwS4YtwJM76hu6AAKA3DEbzCXISsu7mXvsA5MsAQADAgADeAADNgQ",
"Az Eredeti Zöld Monster Energy": "AgACAgIAAyEGAASBdOsgAAIKJGbYwk_-E76j8ram7ON_rSm0WI7jAAK83zEbzCXISm-IrEEfTOnWAQADAgADeAADNgQ",
"Zéró Cukor Ultra azaz a Fehér Monster": "AgACAgIAAyEGAASBdOsgAAIF6WbYbTdxAbYV_2x8WRFGDBV71eCpAAJk3DEbzCXISsvcqSd7X6GgAQADAgADeAADNgQ",
"Monster Rehab Barackos Jeges Tea": "AgACAgIAAx0ES6HB6gABAffPZtlacIjd4Lx0lyr3zeZ8x1HIghIAApPeMRtJJslKzdZ43XwcvgEBAAMCAAN4AAM2BA",
"VR46 azaz A Doktor Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
"Zéró-Cukor Ultra Watermelon": "AgACAgIAAyEGAASBdOsgAAIF12bYbKp8ss_Yv4LyXLcRR8HRWpNKAAJU3DEbzCXISgtk5JiOQiNZAQADAgADeAADNgQ",
"Zéró Cukor - Ultra Fiesta Mango": "AgACAgIAAyEGAASBdOsgAAIKbGbZWU561u3jYmudItvfqPPbyl15AALV3zEbzCXQSpaYcICVgirKAQADAgADeAADNgQ",
"Zéró Cukor - Ultra Paradise": "AgACAgIAAyEGAASBdOsgAAIFuWbYa3g1J9xGstVi7rxV2ARk10x1AAJD3DEbzCXISoOucwksvtBjAQADAgADeAADNgQ",
"Zéró Cukor Ultra Gold Pineapple": "AgACAgIAAyEGAASBdOsgAAIHAmbYcKa5ogiqXwMDyin_nEHBmIjPAALU3DEbzCXISnNMFdNa_ZTxAQADAgADeAADNgQ",
"Zéró Cukor Ultra Rosá": "AgACAgIAAyEGAASBdOsgAAIHZWbYf8pCxOqhnO_E-xyv--EKjCJ9AAJK3TEbzCXISotByecKAZ-SAQADAgADeAADNgQ",
"Juiced Monster Aussie Style Lemonade": "AgACAgIAAyEGAASBdOsgAAIHO2bYf5qnZzp_PUkre-tCTvaEVjiSAAJD3TEbzCXISspdK8If6VG7AQADAgADeAADNgQ",
"Monster Rehab Jeges Tea & Limonádé": "AgACAgIAAyEGAASBdOsgAAILq2bZmCoEJ_1FYZnuBu_735PE-kYtAAKz3DEbxZfRSt_7kRRkze4hAQADAgADeAADNgQ",
"Monster Superfuel Subzero": "AgACAgIAAyEGAASBdOsgAAILrGbZmC9r4dnISSP4qTe0O_MuBz5AAAK03DEbxZfRSo7UYReaz4OvAQADAgADeAADNgQ",
"Monster Superfuel Mean Green": "AgACAgIAAyEGAASBdOsgAAIIxGbYgWoCHBJ5-ulGOq8d_RRD34cGAAJ63TEbzCXISqISJtKn219OAQADAgADeAADNgQ",
"Monster Ultra White senza zucchero": "AgACAgIAAyEGAASBdOsgAAIGrGbYbtSc_gEKKRR-n48sBKPfy1j5AAKk3DEbzCXISiKoCPGkDn8lAQADAgADeAADNgQ",
"Monster Energy Absolutely Zero": "AgACAgIAAyEGAASBdOsgAAIKqGbZXa8TlT3d4eEvHxwTGqOkBPo9AALi3zEbzCXQSscAAQth1dJ3awEAAwIAA3gAAzYE",
"The Doctor": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
"Monster Ultra Red senza zucchero": "AgACAgIAAyEGAASBdOsgAAIIK2bYgMV_QTZSJl_88AaKz9OgEyJ3AAJo3TEbzCXISpJ4XyyDuvunAQADAgADeAADNgQ",
"Monster Ultra Paradise senza zucchero": "AgACAgIAAyEGAASBdOsgAAILsmbZmFF_9njGWvqL9p6sLaX_vaArAAK13DEbxZfRSkYOO4HXOWbxAQADAgADeAADNgQ",
"Monster Ultra Golden Pineapple senza zucchero": "AgACAgIAAyEGAASBdOsgAAILs2bZmFVmEC-Z0gv1PrzCAccRnPALAAK23DEbxZfRSlTxddtG5C5CAQADAgADeAADNgQ",
"Monster Energy Rehab Tea + Limonata": "AgACAgIAAyEGAASBdOsgAAILtGbZmFrAGp5nZNcUhcuRf03t-h-RAAK33DEbxZfRShE-JJW-0bWyAQADAgADeAADNgQ",
"モンスターエナジー": "AgACAgIAAx0ES6HB6gABAfdUZthu0su6xCttsF7K0R5GUSCRSckAAs_gMRtJJsFKhTO-ubjRoj8BAAMCAAN4AAM2BA",
"モンスター ウルトラ": "AgACAgIAAyEGAASBdOsgAAIGgmbYblPj6vzLV8KAs5jrG14HSDtEAAKZ3DEbzCXISh18MSpOv3NoAQADAgADeAADNgQ",
"モンスター マンゴーロコ": "AgACAgIAAyEGAASBdOsgAAIH6WbYgH5I8aZA1-s8u5ILYcb7VCBfAAJg3TEbzCXISmo9LWjf7kiAAQADAgADeAADNgQ",
"モンスター パイプラインパンチ": "AgACAgIAAyEGAASBdOsgAAILuGbZmG2xWOGsmh3chZ-1dNZhxo3bAAK43DEbxZfRSk3SGHXnOuKPAQADAgADeAADNgQ",
"モンスターエナジー ゼロシュガー": "AgACAgIAAyEGAASBdOsgAAIGnWbYbsDoNgwfP0kojqKfHPG6AsLLAAKg3DEbzCXISh7uvgoLapSjAQADAgADeAADNgQ",
"モンスターエナジー 缶500ml": "AgACAgIAAyEGAASBdOsgAAIJhWbYiSSNG2iPlzGYOj3ad1ENAAGL4AACzt0xG8wlyEoc95TjvkHiMAEAAwIAA3gAAzYE",
"モンスター ウルトラバイオレット": "AgACAgIAAyEGAASBdOsgAAIHm2bYgAwGl_yy1U_otwGzHfsMj4k4AAJU3TEbzCXISs7AHAy8eEaJAQADAgADeAADNgQ",
"モンスター パピヨン": "AgACAgIAAyEGAASBdOsgAAIGu2bYbuyDhodpL1Rlu30d4M9QyJ06AAKo3DEbzCXISpf-dx7ePKPOAQADAgADeAADNgQ",
"モンスターエナジー M3": "AgACAgIAAyEGAASBdOsgAAIJwmbYv9XoGzocU3-kPRQG5dMGyW1qAAKY3zEbzCXISsCKIBIv5u2zAQADAgADeAADNgQ",
"モンスターエナジーボトル缶500ml": "AgACAgIAAyEGAASBdOsgAAII_WbYga3_O1O7KQABT2ApQfTLPGRntwACgd0xG8wlyEptLKDfrDSOHwEAAwIAA3gAAzYE",
"モンスター スーパーコーラ": "AgACAgIAAx0ES6HB6gABAfeZZtlZqViAkfRvf-AN2vGdI6pH30gAAoXeMRtJJslKx2Wpzx1J-bgBAAMCAAN4AAM2BA",
"モンスター ウルトラパラダイス": "AgACAgIAAyEGAASBdOsgAAIGl2bYbrlUBzmZx-pHpUJNHWvdERTAAAKe3DEbzCXISsuWwUkNLhHXAQADAgADeAADNgQ",
"Zero-Sugar Ultra / Ultra a.k.a. De Witte Monster": "AgACAgIAAyEGAASBdOsgAAIF6WbYbTdxAbYV_2x8WRFGDBV71eCpAAJk3DEbzCXISsvcqSd7X6GgAQADAgADeAADNgQ",
"Den originale - Green Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Ultra Fiesta Uten Sukker": "AgACAgIAAyEGAASBdOsgAAIJgmbYiSDA7KKXa9VAGEOiX7DqD11dAALN3TEbzCXISnYF-fCZesV4AQADAgADeAADNgQ",
"Ultra Gold Uten Sukker": "AgACAgIAAyEGAASBdOsgAAIFzmbYa4xRbbrUbQoxaowcZ2euAixcAAJK3DEbzCXISqlre8gMaqy4AQADAgADeAADNgQ",
"Ultra Paradise Uten Sukker": "AgACAgIAAyEGAASBdOsgAAIKKmbYwld2dCAFcmZ9xau-a_E-D3pMAAK-3zEbzCXISsMGMjZ_LCpaAQADAgADeAADNgQ",
"Ultra Watermelon Uten Sukker": "AgACAgIAAyEGAASBdOsgAAIKDWbYwMnAyYY10-Rhl1d-pxv8j8MFAAK03zEbzCXISrHgjRwSjAPoAQADAgADeAADNgQ",
"Ultra a.k.a. Hvit Monster Uten Sukker": "AgACAgIAAyEGAASBdOsgAAIJ8mbYwJoTG5rB9QpeSIaLfSWx_JYfAAKz3zEbzCXISjaPjcNz_aEOAQADAgADeAADNgQ",
"Ultra Rosá Uten Sukker": "AgACAgIAAyEGAASBdOsgAAIGFmbYbYPa6mOQB0Ro8IvMVc8wl--_AAJ03DEbzCXISmBr9r4wDc44AQADAgADeAADNgQ",
"Ultra Black Uten Sukker    ": "AgACAgIAAx0ES6HB6gABAfdKZthuraH4_QpUZsbXpOGdGyvx9KgAAszgMRtJJsFK511rVYy2SjEBAAMCAAN4AAM2BA",
"Ultra Peachy Keen Uten Sukker": "AgACAgIAAx0ES6HB6gABAfevZtlaSv_0_BVUS-snPqmoeDwAAe4QAAKO3jEbSSbJSl07294_qGzpAQADAgADeAADNgQ",
"Monster Green Zero Cukru": "AgACAgIAAyEGAASBdOsgAAILy2bZmLomEkMsUXEUG-EWC81NS8JAAAK93DEbxZfRSorpPpihAAFRfQEAAwIAA3gAAzYE",
"Ultra Peachy Keen Bez Cukru    ": "AgACAgIAAyEGAASBdOsgAAIH2mbYgG5JHaT_MJLiHMoc6EWXgZ6yAAJc3TEbzCXISk4uFgd7FjtWAQADAgADeAADNgQ",
"Oryginalny zielony Monster Energy": "AgACAgIAAyEGAASBdOsgAAIJZGbYiPlWMuQaPQJBAAGso9q_sSgmHQACx90xG8wlyEpM3SZTiR66WQEAAwIAA3gAAzYE",
"VR46, czyli Monster Energy The Doctor": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
"Ultra, czyli Biały Monster": "AgACAgIAAyEGAASBdOsgAAIHiWbYf_nsAuQSn09UQ12h4URmzroPAAJQ3TEbzCXISvnjuiKjdcCbAQADAgADeAADNgQ",
"Ultra Fiesta Mango Bez Cukru": "AgACAgIAAyEGAASBdOsgAAIGN2bYbbUSqyJwobtct-0o2FJLU_ALAAJ83DEbzCXISthnVTIDyVR3AQADAgADeAADNgQ",
"Ultra Violet Bez Cukru, czyli Fioletowy Monster": "AgACAgIAAyEGAASBdOsgAAII-mbYgadUuaWAAdflfjhR6DdvIvAyAAKA3TEbzCXISvX2Ujoapg2eAQADAgADeAADNgQ",
"Ultra Strawberry Dreams Bez Cukru  ": "AgACAgIAAyEGAASBdOsgAAIL0mbZmNe_1bv37YuQ1z2fERcgAl17AAK-3DEbxZfRSo-Dvflvs4hdAQADAgADeAADNgQ",
"Ultra Black Bez Cukru": "AgACAgIAAyEGAASBdOsgAAIK92bZYNAu2GvEmjKD7zOJP51kqaawAALz3zEbzCXQStN_ssN4g-UaAQADAgADeAADNgQ",
"Monster Energy Original": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Monster Energy Rehab": "AgACAgIAAyEGAASBdOsgAAIIN2bYgNbOjEYr3smE0th7ZbdYwQYgAAJr3TEbzCXISlox_rhZn0gzAQADAgADeAADNgQ",
"Monster Energy Original Verde": "AgACAgIAAyEGAASBdOsgAAIL1mbZmOZBq-4lt4W3J4D5iJZDjgE4AALA3DEbxZfRSp9mrfsAAcgOkAEAAwIAA3gAAzYE",
"Originalul Monster Energy Zero-Zahăr": "AgACAgIAAyEGAASBdOsgAAIL12bZmOrcq49zwnnRn8VRGieybR--AALB3DEbxZfRSm9qM0durd3rAQADAgADeAADNgQ",
"Ultra a.k.a. Monster Alb": "AgACAgIAAyEGAASBdOsgAAIF6WbYbTdxAbYV_2x8WRFGDBV71eCpAAJk3DEbzCXISsvcqSd7X6GgAQADAgADeAADNgQ",
"Ultra Fiesta Mango Zero-Zahăr": "AgACAgIAAyEGAASBdOsgAAIJoWbYv651O0Yyu9MnxpCEHIdeiPm5AAKW3zEbzCXISv2QQYbub982AQADAgADeAADNgQ",
"Ultra Paradise Zero-Zahăr": "AgACAgIAAyEGAASBdOsgAAIINGbYgNITVQt2_ptIOYTXCXo5enygAAJq3TEbzCXISltvE9Vbsq5ZAQADAgADeAADNgQ",
"Ultra Watermelon Zero Zahăr": "AgACAgIAAyEGAASBdOsgAAIJZ2bYiP8BONAcV9W54zL555ZHVFk3AALI3TEbzCXISsN1PEinsAECAQADAgADeAADNgQ",
"Ultra Golden Pineapple Zero-Zahăr": "AgACAgIAAyEGAASBdOsgAAIGi2bYbpRvw9Wh2LiSy3gFevEH7vD3AAKc3DEbzCXISkpcmfyd5JPVAQADAgADeAADNgQ",
"Original Zeleni Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Orginalet - Green Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Reserve Pineapple": "AgACAgIAAyEGAASBdOsgAAIGvmbYbvDKraB1JWkG911ac0o9n6xNAAKp3DEbzCXISlIhyEua2Wc0AQADAgADeAADNgQ",
"Originalet - Zero Sugar Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGZ2bYbhVAg8OGjYOgoeBv2ZzZdvG1AAKT3DEbzCXISpYGB1d4rcoLAQADAgADeAADNgQ",
"Originalni Monster Energy brez sladkorja": "AgACAgIAAyEGAASBdOsgAAIHlWbYgAapRPhgv_lKsLOkQPy1RFWsAAJT3TEbzCXISkK7zNODb_yOAQADAgADeAADNgQ",
"Monster Energy VR46": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
"Originálny zelený Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Класичний Зелений Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGBGbYbWlhOrzab-Vx5Ay73hF0F4FBAAJu3DEbzCXISpAJbuo4T_72AQADAgADeAADNgQ",
"Ультра, a.k.a Білий Monster": "AgACAgIAAyEGAASBdOsgAAIF6WbYbTdxAbYV_2x8WRFGDBV71eCpAAJk3DEbzCXISsvcqSd7X6GgAQADAgADeAADNgQ",
"Juiced Monster Mucho Loco": "AgACAgIAAx0ES6HB6gABAffnZtmB6_YbyQABIj5phXxai14mEPHWAAJi4zEbGmbJSiCAxLLdnpdTAQADAgADeAADNgQ",
"The Non-Alcoholic Monster Mule": "AgACAgIAAyEGAASBdOsgAAIKVGbZWTR-t5F6yczALWEOeKs0pSl0AALU3zEbzCXQSrY8b9NF0B-1AQADAgADeAADNgQ",
"The Original Absolutely Zero Monster Energy": "AgACAgIAAyEGAASBdOsgAAIL6GbZmS32i0rdD6kD98kVvCPjJhg6AALD3DEbxZfRSnEFAAHsUhOXIgEAAwIAA3gAAzYE",
"Juiced Monster Mariposa": "AgACAgIAAyEGAASBdOsgAAIIoGbYgUfwUPIxaKYPsKeIUhFCxb2VAAJ43TEbzCXIShl_J2WXZ5hIAQADAgADeAADNgQ",
"Monster Rehab Lemon": "AgACAgIAAx0ES6HB6gABAfddZthu8UhzpX9N-97mR3gn23dRL2IAAtHgMRtJJsFKojI7ZvzPmQoBAAMCAAN4AAM2BA",
"Monster Rehab Peach": "AgACAgIAAyEGAASBdOsgAAIJ1GbYwHZW49385-jZ9Fs-HlvpXvevAAKw3zEbzCXISmR6LiJEY-lIAQADAgADeAADNgQ"
}

def dominant_color(image):
    width, height = 150,150
    image = image.resize((width, height),resample = 0)
    #Get colors from image object
    pixels = image.getcolors(width * height)
    #Sort them by count number(first element of tuple)
    sorted_pixels = sorted(pixels, key=lambda t: t[0])
    #Get the most frequent color
    dominant_color = sorted_pixels[-1][1]
    return dominant_color
 
def make(source, clr):
    frames = 10
    resolution = (256, 256)
    delay = 20
    images = []
    base = source.convert('RGBA').resize(resolution)

    for i in range(frames):
        squeeze = i if i < frames/2 else frames - i
        width = 0.8 + squeeze * 0.02
        height = 0.8 - squeeze * 0.05
        offsetX = (1 - width) * 0.5 + 0.1
        offsetY = (1 - height) - 0.08

        canvas = Image.new('RGBA', size=resolution, color=clr)
        canvas.paste(base.resize((round(width * resolution[0]), round(height * resolution[1]))), (round(offsetX * resolution[0]), round(offsetY * resolution[1])))
        with Image.open(resource_stream(__name__, f"pet/pet{i}.gif")).convert('RGBA').resize(resolution) as pet:
            canvas.paste(pet, mask=pet)
        images.append(canvas)
    bio = BytesIO()
    bio.name = 'result.gif'
    save_transparent_gif(images, durations=20, save_file=bio)
    bio.seek(0)
    return bio

def to_fixed(f: float, n=0):
    a, b = str(f).split('.')
    return '{}.{}{}'.format(a, b[:n], '0'*(n-len(b)))

def set_reaction(chat,message,reaction,big = False):
    react = json.dumps([{
        "type": "emoji",
        "emoji": reaction
    }])
    dat = {
        "chat_id": chat,
        "message_id": message,
        "reaction": react,
        "is_big": big
    }
    with requests.Session() as s:
        link = f"https://api.telegram.org/bot{token}/setMessageReaction"
        p = s.post(link, data=dat)
        print(p.json())

def del_reaction(chat,message):
    dat = {
        "chat_id": chat,
        "message_id": message,
    }
    with requests.Session() as s:
        link = f"https://api.telegram.org/bot{token}/setMessageReaction"
        p = s.post(link, data=dat)
        print(p.json())

def get_pil(fid):
    file_info = bot.get_file(fid)
    downloaded_file = bot.download_file(file_info.file_path)
    im = Image.open(BytesIO(downloaded_file))
    return im

def get_bio_link(link):
    bio = BytesIO()
    bio.name = 'result.png'
    with requests.Session() as s:
        p = s.get(link, impersonate="chrome110")
    bio.write(p.content)
    bio.seek(0)
    return bio

def send_pil(im):
    bio = BytesIO()
    bio.name = 'result.png'
    im.save(bio, 'PNG')
    bio.seek(0)
    return bio

def draw_text_rectangle(draw,text,rect_w,rect_h,cord_x,cord_y):
    text = text.upper()
    lines = textwrap.wrap(text, width=16)
    text = '\n'.join(lines)
    selected_size = 1
    for size in range(1, 150):
        arial = ImageFont.FreeTypeFont('comicbd.ttf', size=size)
        #w, h = arial.getsize(text)
        w, h = draw.multiline_textsize(text=text,font=arial,spacing=0)
        if w > rect_w or h > rect_h:
            break 
        selected_size = size   
    arial = ImageFont.FreeTypeFont('comicbd.ttf', size=selected_size)
    draw.multiline_text((cord_x, cord_y), text, fill='black', anchor='mm', font=arial, align='center', spacing=0)

def answer_callback_query(call,txt,show = False):
    try:
        bot.answer_callback_query(call.id,text = txt,show_alert = show)
    except:
        if show:
            try:
                bot.send_message(call.from_user.id, text = txt)
            except:
                pass

@bot.message_handler(commands=["start"])
def msg_start(message):
    return

@bot.message_handler(commands=["monster"])
def msg_monster(message):
    item = random.choice(list(monsters_db.items()))
    bot.send_photo(message.chat.id, photo=item[1], caption=item[0], reply_to_message_id=message.message_id)

@bot.message_handler(commands=["test"])
def msg_test(message):
    m = bot.send_photo(NEKOSLAVIA_CHATID, photo='AgACAgIAAxkBAAMbZqkcVrdd4uf2Aok1WIYOEqRKLPsAApLeMRs0KUhJMW2ULgABMKmXAQADAgADeAADNQQ')
    react_id.append(m.id)
    
@bot.message_handler(commands=["del"])
def msg_del(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)

@bot.message_handler(commands=["pet"])
def msg_pet(message):
        if message.reply_to_message is None:
            bot.send_message(message.chat.id, 'Ответом на сообщение еблан',reply_to_message_id=message.message_id)
            return
        r = bot.get_user_profile_photos(message.reply_to_message.from_user.id)
        if len(r.photos) == 0:
            bot.send_message(message.chat.id, 'У этого пидора нет авы',reply_to_message_id=message.message_id)
            return
        fid = r.photos[0][-1].file_id
        img = get_pil(fid)
        mean = dominant_color(img)
        f = make(img, mean)
        bot.send_animation(message.chat.id,f,reply_to_message_id=message.reply_to_message.message_id)

@bot.message_handler(commands=["say"])
def msg_say(message):
        if message.reply_to_message is None or (message.reply_to_message.text is None and message.reply_to_message.photo is None):
            bot.send_message(message.chat.id, 'Ответом на текст или фото еблан',reply_to_message_id=message.message_id)
            return
        if message.reply_to_message.photo is None:
            with Image.open('necoarc.png') as img:
                draw = ImageDraw.Draw(img)
                draw_text_rectangle(draw, message.reply_to_message.text, 220, 106, 336, 80)
                bot.add_sticker_to_set(user_id=7258570440, name='sayneko_by_NekocringeBot', emojis='🫵',png_sticker=send_pil(img))
                sset = bot.get_sticker_set('sayneko_by_NekocringeBot')
                bot.send_sticker(message.chat.id, sset.stickers[-1].file_id)
        else:
            with Image.open('necopic.png') as im2:
                im1 = get_pil(message.reply_to_message.photo[-1].file_id)
                im1 = im1.resize((253, 169),  Image.ANTIALIAS)
                im0 = Image.new(mode = 'RGB',size = (512,512))
                im0.paste(im1.convert('RGB'), (243,334))
                im0.paste(im2.convert('RGB'), (0,0), im2)
                bot.add_sticker_to_set(user_id=7258570440, name='sayneko_by_NekocringeBot', emojis='🫵',png_sticker=send_pil(im0))
                sset = bot.get_sticker_set('sayneko_by_NekocringeBot')
                bot.send_sticker(message.chat.id, sset.stickers[-1].file_id)

@bot.message_handler(commands=["cube"])
def msg_cube(message):
        if message.reply_to_message is None:
            bot.send_message(message.chat.id, 'Ответом на сообщение еблан',reply_to_message_id=message.message_id)
            return
        r = bot.get_user_profile_photos(message.reply_to_message.from_user.id)
        if len(r.photos) == 0:
            bot.send_message(message.chat.id, 'У этого пидора нет авы',reply_to_message_id=message.message_id)
            return
        fid = r.photos[0][-1].file_id
        file_info = bot.get_file(fid)
        downloaded_file = bot.download_file(file_info.file_path)
        bio = BytesIO(downloaded_file)
        bio.name = 'result.png'
        bio.seek(0)
        direct = random.choice(['left','right'])
        dat = {
            "target": 1,
            "MAX_FILE_SIZE": 1073741824,
            "speed": "ufast",
            "bg_color": "000000",
            "direction": direct
        }
        mp = CurlMime()
        mp.addpart(
            name="image[]",
            content_type="image/png",
            filename="result.png",
            data=bio.getvalue()
        )
        with requests.Session() as s:
            p = s.get("https://en.bloggif.com/cube-3d", impersonate="chrome110")
            soup = BeautifulSoup(p.text, 'lxml')
            tkn = soup.find('form')
            linkfrm = "https://en.bloggif.com" + tkn['action']
            p = s.post(linkfrm, data=dat, multipart=mp, impersonate="chrome110")
            soup = BeautifulSoup(p.text, 'lxml')
            img = soup.find('a', class_='button gray-button')
            linkgif = "https://en.bloggif.com" + img['href']
            p = s.get(linkgif, impersonate="chrome110")
            bio = BytesIO(p.content)
            bio.name = 'result.gif'
            bio.seek(0)
            bot.send_animation(message.chat.id,bio,reply_to_message_id=message.reply_to_message.message_id)

@bot.message_handler(commands=["paint"])
def msg_paint(message):
            markup = telebot.types.InlineKeyboardMarkup()
            button1 = telebot.types.InlineKeyboardButton("Рисовать 🎨", url=f'https://t.me/NekocringeBot/paint')
            markup.add(button1)
            bot.send_message(message.chat.id,'Нажми на кнопку чтобы отправить свой уебанский рисунок', reply_markup=markup)

@bot.message_handler(commands=["sex"])
def msg_sex(message):
        k = random.randint(1,2)
        if k == 1:
            bot.send_animation(message.chat.id,r'https://media.tenor.com/4Vo4wct2us0AAAAC/yes-cat.gif', reply_to_message_id=message.message_id)
        else:
            bot.send_animation(message.chat.id,r'https://media.tenor.com/bQLaiLcbKrMAAAAC/no-sex-cat.gif', reply_to_message_id=message.message_id)

def handle_photo(message):
    if message.chat.id == SERVICE_CHATID:
        bot.send_message(message.chat.id,str(message.photo[-1].file_id) + ' ' + str(message.photo[-1].file_size) + ' ' + bot.get_file_url(message.photo[-1].file_id), reply_to_message_id=message.message_id)
    elif message.chat.id == message.from_user.id:
        img = get_pil(message.photo[-1].file_id)
        img = img.filter(ImageFilter.GaussianBlur(20))
        data = cursor.execute(f"INSERT INTO clicker_media (media, author) VALUES ('{message.photo[-1].file_id}', {message.from_user.id}) RETURNING id")
        data = data.fetchone()
        idk = data[0]  
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        callback_button1 = types.InlineKeyboardButton(text = '💸 Открыть за 300 некокоинов 💸',callback_data = f'pay {idk}')
        keyboard.add(callback_button1)
        bot.send_photo(NEKOSLAVIA_CHATID, send_pil(img), reply_markup=keyboard)

def handle_text(message, txt):
        low = txt.lower()
        '''
        if message.from_user.id in nekosas:
            args = nekosas[message.from_user.id]
            dr_day = args[0]
            dr_month = args[1]
            cur = datetime.fromtimestamp(time.time() + TIMESTAMP)
            if cur.day == dr_day and cur.month == dr_month:
                bot.send_message(message.chat.id, 'Именинника спросить забыли',reply_to_message_id=message.message_id)
                return
        '''
        if message.reply_to_message is not None and message.reply_to_message.from_user.id == BOT_ID:
            bot.send_message(message.chat.id, 'Хохла спросить забыли',reply_to_message_id=message.message_id)
        elif message.chat.id == message.from_user.id:
            bot.send_message(NEKOSLAVIA_CHATID, f'Кто-то высрал: {txt}')
        elif '@all' in low:
            slavoneki = [5417937009,460507186,783003689,540255407,523497602,503671007,448214297,729883976,7258570440,689209397]
            if message.from_user.id in slavoneki:
                slavoneki.remove(message.from_user.id)
            random.shuffle(slavoneki)
            txt = '<b>Д Е Б И Л Ы</b>\n'
            for debil in slavoneki:
                txt += f'<a href="tg://user?id={debil}">᠌᠌</a>'
            txt += '\n<b>П Р И З В А Н Ы</b>'
            bot.send_message(message.chat.id, text = txt,reply_to_message_id=message.message_id)
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEKhutlKvTvRWMv4htVFHb9vgAB1e6EsyUAAts4AAKQulhJOASe1-BSES0wBA')
        elif low == 'база':
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEJqU1krYllZmDsM70Wflt5oZ3-_DwKdAACqBoAAqgrQUv0qGwOc3lWNi8E')
        elif low == 'кринж':
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEJqU9krYl2-rfaY7UQB_35FDwm1FBL9wACvxoAAuorQEtk0hzsZpp1hi8E')
        elif search(r'\bдавид',low):
            bot.send_message(message.chat.id, 'Давид шедевр',reply_to_message_id=message.message_id)
        elif 'негр' in low or 'нигер' in low:
            set_reaction(message.chat.id, message.id, "💅")
        elif search(r'\bсбу\b',low):
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEKWrBlDPH3Ok1hxuoEndURzstMhckAAWYAAm8sAAIZOLlLPx0MDd1u460wBA',reply_to_message_id=message.message_id)
        elif search(r'\bпоро[хш]',low) or search(r'\bрошен',low) or search(r'\bгетьман',low):
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEK-splffs7OZYtr8wzINEw4lxbvwywoAACXSoAAg2JiEoB98dw3NQ3FjME',reply_to_message_id=message.message_id)
        elif search(r'\bзеленс',low):
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELGOplmDc9SkF-ZnVsdNl4vhvzZEo7BQAC5SwAAkrDgEr_AVwN_RkClDQE',reply_to_message_id=message.message_id)
        elif search(r'\bнеко.?арк',low) or search(r'\bneco.?arc',low):
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELHUtlm1wm-0Fc-Ny2na6ogFAuHLC-DgAChisAAgyUiEose7WRTmRWsjQE',reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda message: True, content_types=['photo','video','document','text','animation'])
def msg_text(message):
    if message.photo is not None:
        handle_photo(message)
    if message.text is not None:
        handle_text(message, message.text)
    if message.caption is not None:
        handle_text(message, message.caption)

def callback_process(call):
    args = call.data.split()
    cmd = args[0]
    if cmd == "pay":
        idk = int(args[1])
        data = cursor.execute(f'SELECT level FROM clicker_users WHERE id = {call.from_user.id}')
        data = data.fetchone()     
        if data is None:
            answer_callback_query(call,'Ты бомж')
            return
        score = data[0]
        if score < 300:
            answer_callback_query(call,'Ты бомж')
            return
        data = cursor.execute(f'SELECT media, author FROM clicker_media WHERE id = {idk}')
        data = data.fetchone()     
        if data is None:
            answer_callback_query(call,'Чет хуйня какая-то')
            return
        media = data[0]
        author = data[1]
        if call.from_user.id == author:
            answer_callback_query(call,'Ты еблан?')
            return
        try:
            bot.send_photo(call.from_user.id, media)
            cursor.execute(f'UPDATE clicker_users SET level = level - 300 WHERE id = {call.from_user.id}')
            cursor.execute(f'UPDATE clicker_users SET level = level + 300 WHERE id = {author}')
            answer_callback_query(call,'Отправил фулл в лс', True)
        except:
            answer_callback_query(call,'Тебе надо первым написать боту в лс', True)


@bot.callback_query_handler(func=lambda call: True)
def callback_get(call):
    strkey = f'{call.message.chat.id} {call.message.message_id}'
    if strkey in blocked_messages or call.from_user.id in blocked_users:
        answer_callback_query(call,'Подожди заебал')
        return
    blocked_messages.append(strkey)
    blocked_users.append(call.from_user.id)
    try:
        callback_process(call)
    finally:
        blocked_messages.remove(strkey)
        blocked_users.remove(call.from_user.id)

@bot.message_handler(func=lambda message: True, content_types=['new_chat_title'])
def msg_title(message):
    bot.send_message(message.chat.id, 'Верни бля',reply_to_message_id=message.message_id)

@bot.message_reaction_handler()
def msg_reaction(event):
    if event.message_id in react_id:
        bot.delete_message(chat_id=event.chat.id, message_id=event.message_id)
        chel = html.escape(event.user.full_name, quote = True)
        idk = event.user.id
        words = ['пиздатое', 'потужное', 'волшебное', 'ебанутое', 'некославное', 'кринжовое', 'базированное']
        bot.send_message(event.chat.id, f'Сегодня с <a href="tg://user?id={idk}">{chel}</a> произойдёт нечто <i>{random.choice(words)}</i> ✨💅')

@app.route('/' + token, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200
    
@app.route('/')
def get_ok():
    return 'ok', 200

@app.route('/send_paint', methods=['POST'])
def send_paint():
        file = request.files.get("file")
        bio = BytesIO()
        bio.name = 'result.png'
        file.save(bio)
        bio.seek(0)
        mp = CurlMime()
        mp.addpart(
            name="file",
            content_type="image/png",
            filename="result.png",
            data=bio.getvalue()
        )
        with requests.Session() as s:
            p = s.post('https://telegra.ph/upload', multipart=mp, impersonate="chrome110")
        keypic = p.json()[0]['src'].replace('/file/','').replace('.png','')
        markup = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton("Дорисовать 🎨", url=f'https://t.me/NekocringeBot/paint?startapp={keypic}')
        markup.add(button1)
        bot.send_photo(NEKOSLAVIA_CHATID, photo=bio, reply_markup=markup)
        return '!', 200

@app.route('/pic/<picid>')
def get_pic(picid):
    bio = get_bio_link(f"https://telegra.ph/file/{picid}.png")
    return send_file(bio, mimetype='image/png')

@app.route('/paint')
def get_paint():
        return render_template("paint.html")

@app.route('/clicker')
def get_clicker():
        return render_template("clicker.html")

@app.route('/clicker/get_info', methods=['POST'])
def clicker_get_info():
        content = request.get_json()
        user_id = content['user_id']
        user_name = content['user_name']
        user_name = html.escape(user_name, quote = True)
        data = cursor.execute(f'SELECT level FROM clicker_users WHERE id = {user_id}')
        data = data.fetchone()     
        if data is None:
            cursor.execute(f"INSERT INTO clicker_users (id, name) VALUES ({user_id}, %s)", user_name)
            return jsonify({"score": 0})
        else:
            cursor.execute(f'UPDATE clicker_users SET name = %s WHERE id = {user_id}', user_name)
            return jsonify({"score": data[0]})

@app.route('/clicker/plus', methods=['POST'])
def clicker_plus_one():
        content = request.get_json()
        user_id = content['user_id']
        score = content['score']
        cursor.execute(f'UPDATE clicker_users SET level = {score} WHERE id = {user_id}')
        return '!', 200

@app.route('/clicker/top')
def clicker_top():
        res = "<table>"
        data = cursor.execute(f'SELECT name, level FROM clicker_users ORDER BY level DESC LIMIT 10')
        data = data.fetchall()
        i = 1
        if data is not None:
            for d in data:
                name = d[0]
                level = d[1]
                if len(name) > 20:
                    name = (name[:20] + '..')
                res += f'<tr><td>{i}. {name}</td><td>{level}</td></tr>'
                i += 1
        res += "</table>"
        return render_template("top.html", top=res)

def updater():
    print('Поток запущен')
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def jobday():
    bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEE3Nhikp10A0x2mXRExbnjP1Rm3m4jvAACpxAAAntFWEgwuu0ea7AOsSQE')
    chat_completion = neuro.chat.completions.create(
        messages=[
            {"role": "system", "content": 'Некославия это крайне развитая страна, граждан которой называют некославы, а мудрого правителя некокинг, её девиз это "Славься Некославия!". Прорывом в генной инженерии стало скрещивание кошек с людьми, в результате чего получились некодевочки и некомальчики, которых очень любят некославы. Некодевочки и некомальчики в рамках космической программы Некославии колонизировали Марс и теперь живут там. Самый популярный энергетик в Некославии называется "розовый монстр". В Некославии используют некомобили - новый вид транспорта, который во всём превосходит обычные машины'},
            {"role": "user", "content": "Напиши короткое необычное пожелание доброго утра для жителей Некославии. Используй только кириллические буквы"}
        ],
        model="llama3-8b-8192"
    )
    response = chat_completion.choices[0].message.content
    print(response)
    if len(response) > 500:
        response = response[:500]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient(StringSession(ses), api_id, api_hash, loop=loop) as client:
        client.start()
        m = client.send_message('@silero_voice_bot', response)
        time.sleep(5)
        m = client.get_messages('@silero_voice_bot', ids=m.id+1)
        bio = BytesIO()
        client.download_media(m, bio)
        bio.seek(0)
        bot.send_voice(NEKOSLAVIA_CHATID, bio)

def jobhour():
    r = random.randint(1,100)
    cur = datetime.fromtimestamp(time.time() + TIMESTAMP)
    if r == 42 and cur.hour > 8:
        m = bot.send_photo(NEKOSLAVIA_CHATID, photo='AgACAgIAAxkBAAMbZqkcVrdd4uf2Aok1WIYOEqRKLPsAApLeMRs0KUhJMW2ULgABMKmXAQADAgADeAADNQQ')
        react_id.append(m.id)

def jobnight():
    bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEKXtllDtEnW5DZM-V3VQpFEnzKY0CTOgACsD0AAhGtWEjUrpGNhMRheDAE')

def jobweek():
    stickers = [
    'CAACAgIAAxkBAAELHSRlmy57tJC9YoKiyAKvL9y-oAEdiQACgxUAAuqKgUvgoYyaWs-hnTQE',
    'CAACAgIAAxkBAAELHRhlmy5lZ3DjqeJcBx1gzqVwPb3gAgACyRYAAqjSgUvZ7sYejHfOlzQE',
    'CAACAgIAAxkBAAELHRplmy5qczsacTL8PVB___-SYoW2KwACNxQAAksbgEvt_JM25B-dozQE',
    'CAACAgIAAxkBAAELHRxlmy5tChW5VDyUyEXWUqfHSTSgjQACohcAArw1gUu9AtlM7MrK8DQE',
    'CAACAgIAAxkBAAELHR5lmy5wBE877qJvNoUZv2qyIK4jOQACbBUAAu4tiEs5QNHnNZ-5BzQE',
    'CAACAgIAAxkBAAELHSBlmy5zlVJNQ1kpJjzLqRJpzvq9XgACWxcAAomDiUu7YG_wPShz4zQE',
    'CAACAgIAAxkBAAELHSJlmy53dhqy1F0QGZbSQV0yWhdL8gACoBYAAgwTgUsYv06y1Bvz1DQE'
    ]
    cur = datetime.fromtimestamp(time.time() + TIMESTAMP)
    if cur.month == 10 and cur.day == 20:
        bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEKiXplLTbsgpfjAo5uSvlAephSFbLDzAACYz4AAnnqaUmMWJC_jc4g1zAE')
    elif cur.month == 9 and cur.day == 11:
        bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEMhVRmnGqkCQ0Xd_Mxr7dV4Srmo7SOUgACTkgAAmEJ6UgJ1BtXpz2UCjUE')
    elif cur.month == 3 and cur.day == 8:
        bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEMhVZmnGrliZIzEqsMogQzsg00RX6GTQAC5lAAAhfW6EjSOEw38QNwYzUE')
    else:
        bot.send_sticker(NEKOSLAVIA_CHATID, stickers[datetime.weekday(cur)])
    for d, m in nekosas:
        if cur.month == m and cur.day == d:
            bot.send_message(NEKOSLAVIA_CHATID, 'У кого-то сегодня др ✨💅')

if __name__ == '__main__':
    random.seed()
    schedule.every().day.at("21:01").do(jobweek)
    schedule.every().day.at("05:01").do(jobday)
    schedule.every(60).minutes.do(jobhour)
    Thread(target=updater).start()
    bot.send_message(ME_CHATID, 'Запущено')
    app.run(host='0.0.0.0',port=80, threaded = True)
