import asyncio
import html
import json
import os
import random
import re
import textwrap
import time
import traceback
from datetime import datetime
from io import BytesIO, StringIO
from threading import Thread

import schedule
import telebot
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bs4 import BeautifulSoup
from curl_cffi import requests, CurlMime
from flask import Flask, request, send_file, jsonify, render_template, send_from_directory
from groq import Groq
from petpetgif.saveGif import save_transparent_gif
from pkg_resources import resource_stream
from sqlalchemy import create_engine
from telebot import types, apihelper
from telegraph import Telegraph
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

time.sleep(3)

username = os.environ['USERNAME']
password = os.environ['PASSWORD']
cursor = create_engine(
    'postgresql://postgres.hdahfrunlvoethhwinnc:gT77Av9pQ8IjleU2@aws-0-eu-central-1.pooler.supabase.com:5432/postgres',
    pool_recycle=280)

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


bot = telebot.TeleBot(token, threaded=True, num_threads=10, parse_mode='HTML', exception_handler=ExHandler())
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
    (11, 3),
    (26, 12)
]

SERVICE_CHATID = -1002171923232
NEKOSLAVIA_CHATID = -1001268892138
ME_CHATID = 7258570440
BOT_ID = 6990957141
TIMESTAMP = 2 * 3600

APP_URL = f'https://nekocringebot.onrender.com/{token}'
app = Flask(__name__)
bot.remove_webhook()
bot.set_webhook(url=APP_URL,
                allowed_updates=['message', 'callback_query', 'message_reaction', 'message_reaction_count'])

react_id = []

monsters_db = {
    "The Original Green Monster Energy": "AgACAgIAAyEGAASBdOsgAAILJGbZlfgH0aTsoWkjbdDjB_N8HdafAAKY3DEbxZfRSgILKPZ8jMj8AQADAgADeAADNgQ",
    "Ultra a.k.a. The White Monster": "AgACAgIAAyEGAASBdOsgAAILJWbZlfxxpkxCjfdjYjYkyZTNfRcmAAKa3DEbxZfRSnIEsDuYqON2AQADAgADeAADNgQ",
    "Java Monster Salted Caramel": "AgACAgIAAyEGAASBdOsgAAILJmbZlgAB2nigZDWVh8GHt2Xal6d9GwACm9wxG8WX0UprNM5HohMFywEAAwIAA3gAAzYE",
    "Juice Monster Mango Loco": "AgACAgIAAyEGAASBdOsgAAILJ2bZlgQdzuTzlmpfwcMPdc29WMsKAAKc3DEbxZfRStna1woedYeQAQADAgADeAADNgQ",
    "Rehab Monster Tea & Lemonade": "AgACAgIAAyEGAASBdOsgAAIGMWbYba6rLcEQDUy4uFoN1BfYV2-QAAJ73DEbzCXISl_YOD2I5z6AAQADAgADeAADNgQ",
    "Ultra Fantasy Ruby Red": "AgACAgIAAyEGAASBdOsgAAIGjmbYbpyEbOrIDsmdreujns32s0AtAAKd3DEbzCXISvDqBd6hFyOGAQADAgADeAADNgQ",
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
    "Ultra Peachy Keen": "AgACAgIAAyEGAASBdOsgAAIKimbZWWiIKdoo6HvE6TDM8E2zOqkpAALX3zEbzCXQSjOrXAYId_6LAQADAgADeAADNgQ",
    "Ultra Watermelon": "AgACAgIAAyEGAASBdOsgAAIF12bYbKp8ss_Yv4LyXLcRR8HRWpNKAAJU3DEbzCXISgtk5JiOQiNZAQADAgADeAADNgQ",
    "Ultra Gold": "AgACAgIAAx0ES6HB6gABAffDZtlaYu9iMaDUtkxFdG759-4NHuEAApLeMRtJJslKmejDofLS2sIBAAMCAAN4AAM2BA",
    "Ultra Sunrise": "AgACAgIAAyEGAASBdOsgAAIJQ2bYiMhQpkSHKZ8_F5NMLnXHe8nyAALB3TEbzCXISveqTD5ymUoWAQADAgADeAADNgQ",
    "Ultra Rosá": "AgACAgIAAyEGAASBdOsgAAILOWbZlkx8WpUbxniS27WqPzEAAcsghwACntwxG8WX0UpvhW8gBleDzAEAAwIAA3gAAzYE",
    "Ultra Violet a.k.a. The Purple Monster": "AgACAgIAAyEGAASBdOsgAAIGGWbYbYeVBUG9ls5iVgJu_cLYeX4JAAJ13DEbzCXISrhSqgmMg3XkAQADAgADeAADNgQ",
    "Ultra Red": "AgACAgIAAyEGAASBdOsgAAIJkWbYiTN3uBvkbW_A4lF9DwHqoe_RAALP3TEbzCXISqXejboaOj5_AQADAgADeAADNgQ",
    "Ultra Blue a.k.a. The Blue Monster": "AgACAgIAAx0ES6HB6gABAfdIZthsjj4oDWEer9wrIOjKtfGof_MAAsDgMRtJJsFKzOm39IlYhGoBAAMCAAN4AAM2BA",
    "Ultra Black": "AgACAgIAAyEGAASBdOsgAAIKw2bZXdChlsNMKBV95FEfV4U6EV_VAALj3zEbzCXQShCZbdavxoDDAQADAgADeAADNgQ",
    "Ultra Strawberry Dreams": "AgACAgIAAyEGAASBdOsgAAIKhGbZWWI6QNzyIOmKPbS5feoW0BgzAALW3zEbzCXQSooXrCNC8oqaAQADAgADeAADNgQ",
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
    "Lewis Hamilton": "AgACAgIAAx0ES6HB6gABAff1ZtmCE2MIhsKeqX-8Rsgnc9NZRJYAAmjjMRsaZslK_IeI9e_GQ8wBAAMCAAN4AAM2BA",
    "Ultra Fiesta Mango": "AgACAgIAAyEGAASBdOsgAAIK2WbZX0NyDDAB99QZQ_YBu4KxqJOkAALm3zEbzCXQSuwiRRSEo33vAQADAgADeAADNgQ",
    "Ultra Paradise": "AgACAgIAAyEGAASBdOsgAAIFuWbYa3g1J9xGstVi7rxV2ARk10x1AAJD3DEbzCXISoOucwksvtBjAQADAgADeAADNgQ",
    "VR46 aka. The Doctor Monster Energy": "AgACAgIAAyEGAASBdOsgAAIGc2bYbj6d2cipTxmhHWlyc0uJnfnVAAKW3DEbzCXIStqSWXWR1Q_vAQADAgADeAADNgQ",
    "Monster Monarch": "AgACAgIAAyEGAASBdOsgAAIJ6WbYwI7yR944kcQvZVwWT0rMqZwRAAKx3zEbzCXISubi8UmSqTaUAQADAgADeAADNgQ",
    "Juiced Monster Mixxd Punch": "AgACAgIAAyEGAASBdOsgAAIGiGbYbpFdEowtWhk7wpb6HEOkQrBlAAKb3DEbzCXISnMmAgg26PqUAQADAgADeAADNgQ",
    "Bad Apple": "AgACAgIAAyEGAASBdOsgAAIHLGbYf4i2_HL0HxCO156nBXag6svrAAJA3TEbzCXIStAgeSpjTtj9AQADAgADeAADNgQ",
    "LH44 Monster Energy": "AgACAgIAAyEGAASBdOsgAAILIWbZYTYRsCkIJcNv1aT9rCsVfglxAAL23zEbzCXQSjChLri5nFs-AQADAgADeAADNgQ",
    "Zero Sugar Monster Energy": "AgACAgIAAyEGAASBdOsgAAILI2bZlfOp1cP2u3jA8J5B6Qf0_QvLAAKX3DEbxZfRSjvK0kfIuRrzAQADAgADeAADNgQ",
    "Monster Mule": "AgACAgIAAyEGAASBdOsgAAIGDWbYbXhaafO7_PLjewpuxgd7tQojAAJx3DEbzCXISrWDvOOiIfAkAQADAgADeAADNgQ",
    "Juiced Monster Ripper": "AgACAgIAAyEGAASBdOsgAAILnWbZl-y26YGYj6vlrxb8th0bbRKYAAKx3DEbxZfRSnHM5K7T17gbAQADAgADeAADNgQ",
    "Monster Superfuel Subzero": "AgACAgIAAyEGAASBdOsgAAILrGbZmC9r4dnISSP4qTe0O_MuBz5AAAK03DEbxZfRSo7UYReaz4OvAQADAgADeAADNgQ",
    "Monster Superfuel Mean Green": "AgACAgIAAyEGAASBdOsgAAIIxGbYgWoCHBJ5-ulGOq8d_RRD34cGAAJ63TEbzCXISqISJtKn219OAQADAgADeAADNgQ",
    "Monster Superfuel Watermelon": "AgACAgIAAyEGAASBdOsgAAIGhWbYbllVlTonRalsipL7CI_71KkhAAKa3DEbzCXISvLd3vnzjofhAQADAgADeAADNgQ",
    "モンスターエナジー M3": "AgACAgIAAyEGAASBdOsgAAIJwmbYv9XoGzocU3-kPRQG5dMGyW1qAAKY3zEbzCXISsCKIBIv5u2zAQADAgADeAADNgQ",
    "Juice Monster Khaos": "AgACAgIAAyEGAASBdOsgAAIMu2bZraraMRKO97btcA7pWbcYYilNAAJy3TEbxZfRSiGmjJ6jIJa_AQADAgADeAADNgQ",
    "Monster Energy Dragon Ice Tea Limão": "AgACAgIAAyEGAASBdOsgAAIMx2bZreBO8TRVb7hDV2nhsfGkQBSsAAKB3TEbxZfRSmP0WKF6_Fz3AQADAgADeAADNgQ",
    "Monster Energy Dragon Ice Tea Pêssego": "AgACAgIAAyEGAASBdOsgAAIMyGbZreRdv8FWTv9V_JDYNNDGayMyAAKC3TEbxZfRSgn1672b5vnqAQADAgADeAADNgQ",
    "Dragon Lemon Ice Tea": "AgACAgIAAyEGAASBdOsgAAIMzGbZrfPOxWLK7XRvH7GYLBiBUWNmAAKG3TEbxZfRSuGVyxeMghN3AQADAgADeAADNgQ",
    "Monster Energy Ultra Citra": "AgACAgIAAyEGAASBdOsgAAIM-WbZrruzUb29TTCGL6-zBMxJ8ES1AAKv3TEbxZfRSnMMJ-2BfZxrAQADAgADeAADNgQ",
    "Espresso- und Milchmonster": "AgACAgIAAyEGAASBdOsgAAINBmbZrvTxAAF-DIhzqos-Xuva_XP9GAACuN0xG8WX0UqTkOagPihlwAEAAwIAA3gAAzYE",
    "Vanille-Espresso-Monster": "AgACAgIAAyEGAASBdOsgAAINB2bZrvhDCTwMa3eKtScpK2tTG9cQAAK53TEbxZfRSl_TjtwImL1pAQADAgADeAADNgQ",
    "Gesalzenes Karamell Espresso-Monster": "AgACAgIAAyEGAASBdOsgAAINCGbZrv5U9pJnrDRmATwAAYN4RtayrQACut0xG8WX0UqZILFz0SUyvQEAAwIAA3gAAzYE",
    "Java Monster Swiss Chocolate": "AgACAgIAAyEGAASBdOsgAAINIWbZr2M7vMhTmZHZLRe22T2byBdDAALI3TEbxZfRSmF4-VSNrFzgAQADAgADeAADNgQ"
}


def dominant_color(image):
    width, height = 150, 150
    image = image.resize((width, height), resample=0)
    # Get colors from image object
    pixels = image.getcolors(width * height)
    # Sort them by count number(first element of tuple)
    sorted_pixels = sorted(pixels, key=lambda t: t[0])
    # Get the most frequent color
    dominant_color = sorted_pixels[-1][1]
    return dominant_color


def make(source, clr):
    frames = 10
    resolution = (256, 256)
    delay = 20
    images = []
    base = source.convert('RGBA').resize(resolution)

    for i in range(frames):
        squeeze = i if i < frames / 2 else frames - i
        width = 0.8 + squeeze * 0.02
        height = 0.8 - squeeze * 0.05
        offsetX = (1 - width) * 0.5 + 0.1
        offsetY = (1 - height) - 0.08

        canvas = Image.new('RGBA', size=resolution, color=clr)
        canvas.paste(base.resize((round(width * resolution[0]), round(height * resolution[1]))),
                     (round(offsetX * resolution[0]), round(offsetY * resolution[1])))
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
    return '{}.{}{}'.format(a, b[:n], '0' * (n - len(b)))


def set_reaction(chat, message, reaction, big=False):
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


def del_reaction(chat, message):
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


def draw_text_rectangle(draw, text, rect_w, rect_h, cord_x, cord_y):
    text = text.upper()
    lines = textwrap.wrap(text, width=16)
    text = '\n'.join(lines)
    selected_size = 1
    for size in range(1, 150):
        arial = ImageFont.FreeTypeFont('comicbd.ttf', size=size)
        # w, h = arial.getsize(text)
        w, h = draw.multiline_textsize(text=text, font=arial, spacing=0)
        if w > rect_w or h > rect_h:
            break
        selected_size = size
    arial = ImageFont.FreeTypeFont('comicbd.ttf', size=selected_size)
    draw.multiline_text((cord_x, cord_y), text, fill='black', anchor='mm', font=arial, align='center', spacing=0)


def answer_callback_query(call, txt, show=False):
    try:
        bot.answer_callback_query(call.id, text=txt, show_alert=show)
    except:
        if show:
            try:
                bot.send_message(call.from_user.id, text=txt)
            except:
                pass


@bot.message_handler(commands=["start"])
def msg_start(message):
    return


@bot.message_handler(commands=["monster"])
def msg_monster(message):
    item = random.choice(list(monsters_db.items()))
    bot.send_photo(message.chat.id, photo=item[1], caption=item[0], reply_to_message_id=message.message_id)


@bot.message_handler(commands=["del"])
def msg_del(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)


@bot.message_handler(commands=["abobus"])
def msg_abobus(message):
    jobnews(SERVICE_CHATID)


@bot.message_handler(commands=["pet"])
def msg_pet(message):
    if message.reply_to_message is None:
        bot.send_message(message.chat.id, 'Ответом на сообщение еблан', reply_to_message_id=message.message_id)
        return
    if message.reply_to_message.photo is None:
        r = bot.get_user_profile_photos(message.reply_to_message.from_user.id)
        if len(r.photos) == 0:
            bot.send_message(message.chat.id, 'У этого пидора нет авы', reply_to_message_id=message.message_id)
            return
        fid = r.photos[0][-1].file_id
        img = get_pil(fid)
    else:
        img = get_pil(message.reply_to_message.photo[-1].file_id)
        img = img.resize((500, 500), Image.ANTIALIAS)
    mean = dominant_color(img)
    f = make(img, mean)
    bot.send_animation(message.chat.id, f, reply_to_message_id=message.reply_to_message.message_id)


@bot.message_handler(commands=["say"])
def msg_say(message):
    if message.reply_to_message is None or (
            message.reply_to_message.text is None and message.reply_to_message.photo is None):
        bot.send_message(message.chat.id, 'Ответом на текст или фото еблан', reply_to_message_id=message.message_id)
        return
    if message.reply_to_message.photo is None:
        with Image.open('necoarc.png') as img:
            draw = ImageDraw.Draw(img)
            draw_text_rectangle(draw, message.reply_to_message.text, 220, 106, 336, 80)
            bot.add_sticker_to_set(user_id=7258570440, name='sayneko_by_NekocringeBot', emojis='🫵',
                                   png_sticker=send_pil(img))
            sset = bot.get_sticker_set('sayneko_by_NekocringeBot')
            bot.send_sticker(message.chat.id, sset.stickers[-1].file_id)
    else:
        with Image.open('necopic.png') as im2:
            im1 = get_pil(message.reply_to_message.photo[-1].file_id)
            im1 = im1.resize((253, 169), Image.ANTIALIAS)
            im0 = Image.new(mode='RGB', size=(512, 512))
            im0.paste(im1.convert('RGB'), (243, 334))
            im0.paste(im2.convert('RGB'), (0, 0), im2)
            bot.add_sticker_to_set(user_id=7258570440, name='sayneko_by_NekocringeBot', emojis='🫵',
                                   png_sticker=send_pil(im0))
            sset = bot.get_sticker_set('sayneko_by_NekocringeBot')
            bot.send_sticker(message.chat.id, sset.stickers[-1].file_id)


@bot.message_handler(commands=["cube"])
def msg_cube(message):
    if message.reply_to_message is None:
        bot.send_message(message.chat.id, 'Ответом на сообщение еблан', reply_to_message_id=message.message_id)
        return
    if message.reply_to_message.photo is None:
        r = bot.get_user_profile_photos(message.reply_to_message.from_user.id)
        if len(r.photos) == 0:
            bot.send_message(message.chat.id, 'У этого пидора нет авы', reply_to_message_id=message.message_id)
            return
        fid = r.photos[0][-1].file_id
        img = get_pil(fid)
    else:
        img = get_pil(message.reply_to_message.photo[-1].file_id)
        img = img.resize((500, 500), Image.ANTIALIAS)
    bio = send_pil(img)
    direct = random.choice(['left', 'right'])
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
        bot.send_animation(message.chat.id, bio, reply_to_message_id=message.reply_to_message.message_id)


@bot.message_handler(commands=["paint"])
def msg_paint(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("Рисовать 🎨", url=f'https://t.me/NekocringeBot/paint')
    markup.add(button1)
    bot.send_message(message.chat.id, 'Нажми на кнопку чтобы отправить свой уебанский рисунок', reply_markup=markup)


@bot.message_handler(commands=["sex"])
def msg_sex(message):
    k = random.randint(1, 2)
    if k == 1:
        bot.send_animation(message.chat.id, r'https://media.tenor.com/4Vo4wct2us0AAAAC/yes-cat.gif',
                           reply_to_message_id=message.message_id)
    else:
        bot.send_animation(message.chat.id, r'https://media.tenor.com/bQLaiLcbKrMAAAAC/no-sex-cat.gif',
                           reply_to_message_id=message.message_id)


def handle_photo(message):
    if message.chat.id == SERVICE_CHATID:
        bot.send_message(message.chat.id, str(message.photo[-1].file_id) + ' ' + str(
            message.photo[-1].file_size) + ' ' + bot.get_file_url(message.photo[-1].file_id),
                         reply_to_message_id=message.message_id)
    elif message.chat.id == message.from_user.id:
        img = get_pil(message.photo[-1].file_id)
        img = img.filter(ImageFilter.GaussianBlur(20))
        data = cursor.execute(
            f"INSERT INTO clicker_media (media, author) VALUES ('{message.photo[-1].file_id}', {message.from_user.id}) RETURNING id")
        data = data.fetchone()
        idk = data[0]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        callback_button1 = types.InlineKeyboardButton(text='💸 Открыть за 300 некокоинов 💸', callback_data=f'pay {idk}')
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
        bot.send_message(message.chat.id, 'Хохла спросить забыли', reply_to_message_id=message.message_id)
    elif message.chat.id == message.from_user.id:
        bot.send_message(NEKOSLAVIA_CHATID, f'Кто-то высрал: {txt}')
    elif '@all' in low:
        slavoneki = [5417937009, 460507186, 783003689, 540255407, 523497602, 503671007, 448214297, 729883976,
                     7258570440, 689209397]
        if message.from_user.id in slavoneki:
            slavoneki.remove(message.from_user.id)
        random.shuffle(slavoneki)
        txt = '<b>Д Е Б И Л Ы</b>\n'
        for debil in slavoneki:
            txt += f'<a href="tg://user?id={debil}">᠌᠌</a>'
        txt += '\n<b>П Р И З В А Н Ы</b>'
        bot.send_message(message.chat.id, text=txt, reply_to_message_id=message.message_id)
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEKhutlKvTvRWMv4htVFHb9vgAB1e6EsyUAAts4AAKQulhJOASe1-BSES0wBA')
    elif low == 'база':
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEJqU1krYllZmDsM70Wflt5oZ3-_DwKdAACqBoAAqgrQUv0qGwOc3lWNi8E')
    elif low == 'кринж' or low == 'криндж' or low == 'cringe':
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEJqU9krYl2-rfaY7UQB_35FDwm1FBL9wACvxoAAuorQEtk0hzsZpp1hi8E')
    elif re.search(r'\bдавид', low):
        bot.send_message(message.chat.id, 'Давид шедевр', reply_to_message_id=message.message_id)
    elif 'негр' in low or 'нигер' in low:
        set_reaction(message.chat.id, message.id, "💅")
    elif re.search(r'\bсбу\b', low):
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEKWrBlDPH3Ok1hxuoEndURzstMhckAAWYAAm8sAAIZOLlLPx0MDd1u460wBA',
                         reply_to_message_id=message.message_id)
    elif re.search(r'\bпоро[хш]', low) or re.search(r'\bрошен', low) or re.search(r'\bгетьман', low):
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEK-splffs7OZYtr8wzINEw4lxbvwywoAACXSoAAg2JiEoB98dw3NQ3FjME',
                         reply_to_message_id=message.message_id)
    elif re.search(r'\bзеленс', low):
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELGOplmDc9SkF-ZnVsdNl4vhvzZEo7BQAC5SwAAkrDgEr_AVwN_RkClDQE',
                         reply_to_message_id=message.message_id)
    elif re.search(r'\bнеко.?арк', low) or re.search(r'\bneco.?arc', low):
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELHUtlm1wm-0Fc-Ny2na6ogFAuHLC-DgAChisAAgyUiEose7WRTmRWsjQE',
                         reply_to_message_id=message.message_id)


@bot.message_handler(func=lambda message: True, content_types=['photo', 'video', 'document', 'text', 'animation'])
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
            answer_callback_query(call, 'Ты бомж')
            return
        score = data[0]
        if score < 300:
            answer_callback_query(call, 'Ты бомж')
            return
        data = cursor.execute(f'SELECT media, author FROM clicker_media WHERE id = {idk}')
        data = data.fetchone()
        if data is None:
            answer_callback_query(call, 'Чет хуйня какая-то')
            return
        media = data[0]
        author = data[1]
        if call.from_user.id == author:
            answer_callback_query(call, 'Ты еблан?')
            return
        try:
            bot.send_photo(call.from_user.id, media)
            cursor.execute(f'UPDATE clicker_users SET level = level - 300 WHERE id = {call.from_user.id}')
            cursor.execute(f'UPDATE clicker_users SET level = level + 300 WHERE id = {author}')
            answer_callback_query(call, 'Отправил фулл в лс', True)
        except:
            answer_callback_query(call, 'Тебе надо первым написать боту в лс', True)


@bot.callback_query_handler(func=lambda call: True)
def callback_get(call):
    if call.game_short_name == 'nekoracing':
        url = f"https://nekocringebot.onrender.com/game?user_id={call.from_user.id}&message_id={call.inline_message_id}"
        bot.answer_callback_query(call.id, url=url)
        return
    strkey = f'{call.message.chat.id} {call.message.message_id}'
    if strkey in blocked_messages or call.from_user.id in blocked_users:
        answer_callback_query(call, 'Подожди заебал')
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
    bot.send_message(message.chat.id, 'Верни бля', reply_to_message_id=message.message_id)


@bot.message_reaction_handler()
def msg_reaction(event):
    if event.message_id in react_id:
        bot.delete_message(chat_id=event.chat.id, message_id=event.message_id)
        chel = html.escape(event.user.full_name, quote=True)
        idk = event.user.id
        words = ['пиздатое', 'потужное', 'волшебное', 'ебанутое', 'некославное', 'кринжовое', 'базированное',
                 '[ДАННЫЕ УДАЛЕНЫ]', 'свеговое']
        bot.send_message(event.chat.id,
                         f'Сегодня с <a href="tg://user?id={idk}">{chel}</a> произойдёт нечто <i>{random.choice(words)}</i> ✨💅')


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
        name="image",
        content_type="image/png",
        filename="result.png",
        data=bio.getvalue()
    )
    with requests.Session() as s:
        p = s.post('https://api.imgbb.com/1/upload?key=3100ff6a118529e2ca934359de29fd46', multipart=mp,
                   impersonate="chrome110")
    keypic = p.json()['data']['url'].split('/')[-2]
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("Дорисовать 🎨",
                                                 url=f'https://t.me/NekocringeBot/paint?startapp={keypic}')
    markup.add(button1)
    bot.send_photo(NEKOSLAVIA_CHATID, photo=bio, reply_markup=markup)
    return '!', 200


@app.route('/pic/<picid>')
def get_pic(picid):
    bio = get_bio_link(f"https://i.ibb.co/{picid}/result.png")
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
    user_name = html.escape(user_name, quote=True)
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


@app.route('/game')
def get_game():
    return render_template("game.html")


@app.route('/game/update_score', methods=['POST'])
def game_update_score():
    content = request.get_json()
    user_id = content['user_id']
    score = content['score']
    message_id = content['message_id']
    try:
        bot.set_game_score(user_id=user_id, score=score, inline_message_id=message_id)
    except:
        pass
    return '!', 200


@app.route('/static/&lt;path:path&gt;')
def send_static(path):
    return send_from_directory('static', path)


def updater():
    print('Поток запущен')
    while True:
        schedule.run_pending()
        time.sleep(1)


def jobday():
    # доброе утро некославы
    bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEE3Nhikp10A0x2mXRExbnjP1Rm3m4jvAACpxAAAntFWEgwuu0ea7AOsSQE')
    chat_completion = neuro.chat.completions.create(
        messages=[
            {"role": "system",
             "content": 'Некославия это крайне развитая страна, граждан которой называют некославы, а мудрого правителя некокинг, её девиз это "Славься Некославия!". Прорывом в генной инженерии стало скрещивание кошек с людьми, в результате чего получились некодевочки и некомальчики, которых очень любят некославы. Некодевочки и некомальчики в рамках космической программы Некославии колонизировали Марс и теперь живут там. Самый популярный энергетик в Некославии называется "розовый монстр". В Некославии используют некомобили - новый вид транспорта, который во всём превосходит обычные машины'},
            {"role": "user",
             "content": "Напиши короткое необычное пожелание доброго утра для жителей Некославии. Используй только кириллические буквы"}
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
        m = client.get_messages('@silero_voice_bot', ids=m.id + 1)
        bio = BytesIO()
        client.download_media(m, bio)
        bio.seek(0)
        bot.send_voice(NEKOSLAVIA_CHATID, bio)
    # скидки на монстры
    link = generate_telegraph_link()
    if link is not None:
        text = "<b>Начни свой день с монстра по скидке</b>"
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        callback_button = types.InlineKeyboardButton(text='Список скидок', url=link)
        keyboard.add(callback_button)
        bot.send_message(NEKOSLAVIA_CHATID, text, reply_markup=keyboard)


def jobnews(channel=-1002426494412):
    # пост в канал
    news = ['спорт', 'финансы', 'технологии', 'международные отношения', 'политика', 'общество', 'наука',
            'красота и здоровье', 'шоу-бизнес', 'компьютерные игры', 'погода', 'мнения', 'астрология', 'туризм',
            'военные действия', 'культура', 'фильмы и сериалы', 'интервью', 'историческая правда', 'проишествия',
            'власть', 'образование', 'криминал', 'разоблачение', 'благотворительность', 'мода', 'ИТ-технологии',
            'кибербезопасность', 'изменение климата', 'медицина', 'выборы', 'коррупция', 'развлечения',
            'социальные сети', 'мистика', 'кулинария', 'история успеха', 'литература и книги', 'развенчивание мифов',
            'архитектура и урбанистика', 'беженцы и мигранты']
    new = random.choice(news)
    chat_completion = neuro.chat.completions.create(
        messages=[
            {"role": "system",
             "content": 'Некославия это крайне развитая страна, граждан которой называют некославы, а мудрого правителя некокинг, её девиз это "Славься Некославия!". Прорывом в генной инженерии стало скрещивание кошек с людьми, в результате чего получились некодевочки и некомальчики, которых очень любят некославы. Некодевочки и некомальчики в рамках космической программы Некославии колонизировали Марс и теперь живут там. Самый популярный энергетик в Некославии называется "розовый монстр". В Некославии используют некомобили - новый вид транспорта, который во всём превосходит обычные машины. Ты администратор новостного канала "Некославач" в телеграмме, в канале открыты комментарии. Твоя работа состоит в том чтобы писать выдуманные новости про Некославию в этот канал. Твой ответ должен быть уникальным, лаконичным, не должен содержать ничего кроме заголовка новости и текста новости без даты.'},
            {"role": "user",
             "content": f'Напиши новость на тему "{new}". Учти что сегодня {datetime.now().strftime("%d.%m.%Y")}'}
        ],
        model="llama-3.3-70b-versatile"
    )
    response = chat_completion.choices[0].message.content
    new = new.replace(' ', '_').replace('-', '_')
    if '\n' in response:
        mas = response.split('\n')
        title = mas[0]
        del mas[0]
        text = ''.join(mas)
        text = f"⚡️<b>{title}</b>⚡️\n\n{text}\n\n#{new}"
    else:
        text = f"{response}\n\n#{new}"
    bot.send_message(channel, text)


def jobhour():
    r = random.randint(1, 100)
    cur = datetime.fromtimestamp(time.time() + TIMESTAMP)
    if r == 42 and cur.hour > 8:
        m = bot.send_photo(NEKOSLAVIA_CHATID,
                           photo='AgACAgIAAxkBAAMbZqkcVrdd4uf2Aok1WIYOEqRKLPsAApLeMRs0KUhJMW2ULgABMKmXAQADAgADeAADNQQ')
        react_id.append(m.id)


def jobnight():
    bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEKXtllDtEnW5DZM-V3VQpFEnzKY0CTOgACsD0AAhGtWEjUrpGNhMRheDAE')


def fetch_silpo():
    with requests.Session() as session:
        for attempts in range(3):
            try:
                result = []
                link = "https://sf-ecom-api.silpo.ua/v1/uk/branches/00000000-0000-0000-0000-000000000000/products?limit=47&offset=0&deliveryType=DeliveryHome&includeChildCategories=true&sortBy=productsList&sortDirection=desc&inStock=true&search=monster%20energ"
                resp = session.get(link, impersonate="chrome110")
                data = resp.json()
                for item in data["items"]:
                    if item["oldPrice"] is None:
                        continue
                    discount = round(float(item["oldPrice"] - item["price"]) / item["oldPrice"] * 100)
                    words = re.findall(r'\b[А-ЯA-Z]\w*\b', item["title"])
                    words.pop(0)
                    title = ' '.join(words)
                    href = f"https://silpo.ua/product/{item['slug']}"
                    result.append(
                        {
                            "title": title,
                            "href": href,
                            "discount": discount,
                            "price": item["price"]
                        }
                    )
                return result
            except:
                time.sleep(3)
        return []


def generate_telegraph_link():
    silpo_data = fetch_silpo()
    atb_data = fetch_atb()
    if len(silpo_data) == 0 and len(atb_data) == 0:
        return None
    text = '<p>'
    if len(silpo_data) != 0:
        text += '<h4>Сильпо</h4>'
        silpo_data = sorted(silpo_data, key=lambda item: item["discount"], reverse=True)
        for item in silpo_data:
            text += f'''<a href="{item['href']}">{item['title']}</a> {item['price']} грн -{item['discount']}%<br>'''
    if len(atb_data) != 0:
        text += '<h4>АТБ</h4>'
        atb_data = sorted(atb_data, key=lambda item: item["discount"], reverse=True)
        for item in atb_data:
            text += f'''<a href="{item['href']}">{item['title']}</a> {item['price']} грн -{item['discount']}%<br>'''
    text += '</p>'
    telegraph = Telegraph()
    telegraph.create_account(short_name='nekocringebot')
    for attempts in range(3):
        try:
            response = telegraph.create_page('Список скидок', html_content=text)
            return response['url']
        except:
            time.sleep(3)


def fetch_atb():
    with requests.Session() as session:
        for attempts in range(3):
            try:
                result = []
                link = "https://www.atbmarket.com/sch?page=1&lang=uk&query=напій%20monster"
                resp = session.get(link, impersonate="chrome110")
                soup = BeautifulSoup(resp.text, 'lxml')
                items = soup.find_all('article', class_='catalog-item')
                for item in items:
                    if item.find('data', class_='product-price__bottom') is None:
                        continue
                    old_price = float(item.find('data', class_='product-price__bottom')['value'])
                    new_price = float(item.find('data', class_='product-price__top')['value'])
                    print(old_price)
                    print(new_price)
                    words = re.findall(r'\b[А-ЯA-Z]\w*\b',
                                       item.find('div', class_='catalog-item__title').find('a').text)
                    words.pop(0)
                    title = ' '.join(words)
                    href = f"https://www.atbmarket.com{item.find('div', class_='catalog-item__title').find('a')['href']}"
                    discount = round((old_price - new_price) / old_price * 100)
                    result.append(
                        {
                            "title": title,
                            "href": href,
                            "discount": discount,
                            "price": new_price
                        }
                    )
                return result
            except:
                time.sleep(3)
        return []


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
    year_stickers = [
        (20, 10, 'CAACAgIAAxkBAAEKiXplLTbsgpfjAo5uSvlAephSFbLDzAACYz4AAnnqaUmMWJC_jc4g1zAE'),
        (11, 9, 'CAACAgIAAxkBAAEMhVRmnGqkCQ0Xd_Mxr7dV4Srmo7SOUgACTkgAAmEJ6UgJ1BtXpz2UCjUE'),
        (8, 3, 'CAACAgIAAxkBAAEMhVZmnGrliZIzEqsMogQzsg00RX6GTQAC5lAAAhfW6EjSOEw38QNwYzUE'),
        (1, 9, 'CAACAgIAAxkBAAENReBnUQMHcjQ1x4JMuDPSGa0PfS_LSAACNlsAAohFiEqr6bR0kH_YYTYE'),
        (1, 6, 'CAACAgIAAxkBAAENReJnUQMKaJfpiXbidjshX1p6lNhusQACFGkAAocUiUoX4YjxSy2hZTYE'),
        (1, 3, 'CAACAgIAAxkBAAENRd5nUQME_x_lNt4Drsb7LHfD06M6dgACN2AAAlfaiEpxGgpWto35JzYE'),
        (1, 12, 'CAACAgIAAxkBAAENRdxnUQL4rW0uNpp5izN8KlbN_gIycgACm18AAg7SiUqY9isavfMggTYE')
    ]
    for d, m in nekosas:
        if cur.month == m and cur.day == d:
            bot.send_message(NEKOSLAVIA_CHATID, 'У кого-то сегодня др ✨💅')
    for d, m, stik in year_stickers:
        if cur.month == m and cur.day == d:
            bot.send_sticker(NEKOSLAVIA_CHATID, stik)
            return
    bot.send_sticker(NEKOSLAVIA_CHATID, stickers[datetime.weekday(cur)])


if __name__ == '__main__':
    random.seed()
    schedule.every().day.at("22:01").do(jobweek)
    schedule.every().day.at("06:01").do(jobday)
    schedule.every(60).minutes.do(jobhour)
    schedule.every(12).hours.do(jobnews)
    Thread(target=updater).start()
    bot.send_message(ME_CHATID, 'Запущено')
    app.run(host='0.0.0.0', port=80, threaded=True)
