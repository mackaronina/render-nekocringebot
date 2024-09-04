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

monsters_db = {}

def get_monsters():
    try:
        links = [
        "https://www.monsterenergy.com/en-us/energy-drinks/",
        "https://www.monsterenergy.com/de-at/energy-drinks/",
        "https://www.monsterenergy.com/en-au/energy-drinks/",
        "https://www.monsterenergy.com/hr-ba/energy-drinks/",
        "https://www.monsterenergy.com/sr-ba/energy-drinks/",
        "https://www.monsterenergy.com/fr-be/energy-drinks/",
        "https://www.monsterenergy.com/nl-be/energy-drinks/",
        "https://www.monsterenergy.com/bg-bg/energy-drinks/",
        "https://www.monsterenergy.com/en-ca/energy-drinks/",
        "https://www.monsterenergy.com/fr-ca/energy-drinks/",
        "https://www.monsterenergy.com/de-ch/energy-drinks/",
        "https://www.monsterenergy.com/fr-ch/energy-drinks/",
        "https://www.monsterenergy.com/it-ch/energy-drinks/",
        "https://www.monsterenergy.com/el-cy/energy-drinks/",
        "https://www.monsterenergy.com/cs-cz/energy-drinks/",
        "https://www.monsterenergy.com/de-de/energy-drinks/",
        "https://www.monsterenergy.com/da-dk/energy-drinks/",
        "https://www.monsterenergy.com/et-ee/energy-drinks/",
        "https://www.monsterenergy.com/es-es/energy-drinks/",
        "https://www.monsterenergy.com/fr-fr/energy-drinks/",
        "https://www.monsterenergy.com/en-gb/energy-drinks/",
        "https://www.monsterenergy.com/el-gr/energy-drinks/",
        "https://www.monsterenergy.com/hr-hr/energy-drinks/",
        "https://www.monsterenergy.com/hu-hu/energy-drinks/",
        "https://www.monsterenergy.com/en-ie/energy-drinks/",
        "https://www.monsterenergy.com/en-in/energy-drinks/",
        "https://www.monsterenergy.com/it-it/energy-drinks/",
        "https://www.monsterenergy.com/ja-jp/energy-drinks/",
        "https://www.monsterenergy.com/lt-lt/energy-drinks/",
        "https://www.monsterenergy.com/lv-lv/energy-drinks/",
        "https://www.monsterenergy.com/nl-nl/energy-drinks/",
        "https://www.monsterenergy.com/no-no/energy-drinks/",
        "https://www.monsterenergy.com/en-nz/energy-drinks/",
        "https://www.monsterenergy.com/pl-pl/energy-drinks/",
        "https://www.monsterenergy.com/pt-pt/energy-drinks/",
        "https://www.monsterenergy.com/ro-ro/energy-drinks/",
        "https://www.monsterenergy.com/sr-rs/energy-drinks/",
        "https://www.monsterenergy.com/sv-se/energy-drinks/",
        "https://www.monsterenergy.com/sl-si/energy-drinks/",
        "https://www.monsterenergy.com/sk-sk/energy-drinks/",
        "https://www.monsterenergy.com/uk-ua/energy-drinks/",
        "https://www.monsterenergy.com/en-us/energy-drinks/",
        "https://www.monsterenergy.com/en-za/energy-drinks/"
        ]
        with requests.Session() as s:
            for link in links:
                    p = s.get(link, impersonate="chrome110")
                    bot.send_message(ME_CHATID, p.status_code)
                    soup = BeautifulSoup(p.text, 'lxml')
                    allm = soup.findAll('div', class_='col-12 col-lg-12')
                    for monster in allm:
                        img = monster.find('img')
                        if img is not None:
                            monsters_db[img['alt']] = img['src']
            time.sleep(3)
        bot.send_message(ME_CHATID, len(monsters_db))
    except Exception as e:
        bot.send_message(ME_CHATID, e)

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
    if len(monsters_db) < 1:
        bot.send_message(message.chat.id, 'Иди нахуй', reply_to_message_id=message.message_id)
        return
    item = random.choice(list(monsters_db.items()))
    bio = get_bio_link(item[1])
    im = Image.open(bio)
    w, h = im.size
    im0 = Image.new(mode='RGB', size=(h,h), color='#FFFFFF')
    im0.paste(im.convert('RGB'), (round((h-w)/2), 0), im)
    bot.send_photo(message.chat.id, photo=send_pil(im0), caption=item[0], reply_to_message_id=message.message_id)

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
    Thread(target=get_monsters).start()
    bot.send_message(ME_CHATID, 'Запущено')
    app.run(host='0.0.0.0',port=80, threaded = True)
