import telebot
from telebot import types
from flask import Flask, request, send_from_directory, send_file, jsonify, render_template, url_for
from petpetgif.saveGif import save_transparent_gif
from io import BytesIO, StringIO
from PIL import Image,ImageDraw,ImageFont, ImageStat
import textwrap
from pkg_resources import resource_stream
from threading import Thread
import time
import schedule
import requests
from bs4 import BeautifulSoup
import random
from re import search
import json
import html
import math
import traceback
from datetime import datetime
import g4f
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio
from sqlalchemy import create_engine
import os

time.sleep(3)

username = os.environ['USERNAME']
password = os.environ['PASSWORD']
cursor = create_engine(f'postgresql://postgres.hdahfrunlvoethhwinnc:gT77Av9pQ8IjleU2@aws-0-eu-central-1.pooler.supabase.com:5432/postgres', pool_recycle=280)

g4f.debug.logging = True
g4f.debug.check_version = False

api_id = 17453825
api_hash = 'aa6df76596b13eb999078e2e9796ff95'
ses = '1ApWapzMBuyCFQo-t4AmnOgFx64Ek9CrNhxMtmCs2f3uQeroLo_3dJ27mGc6ASiThsRk4XWZM_I1m0aHB_DKKM-eVJ_YvaxhSbrWerhXJtxB3pZwo_DnCG8G8zKCdVcNRwDUbfJNfM92853b6XevUkYwMwzR8wWLbR-HtTyQqMrygoRld4D4vtz5Yfe5PuukjeqAJq9CDQQkY9ohgnpazJo83vBnirt_WPIV9NJeC1lQBULBhevUWVMfr8kz0XuW0klWpZyE8135a7hafzVEpcf5Zlu53-t-0rIYe-R5uuiZEz2uJoRdFoXIsI7jyTeBwb_Yw98bBtgf_NtSaGv-RVE2x_En7DBk='

token = '6964908043:AAE0fSVJGwNKOQWAwQRH6QDfuuXZx2EQNME'
class ExHandler(telebot.ExceptionHandler):
    def handle(self, exc):
        bot.send_message(ME_CHATID, traceback.format_exc())
        return True
bot = telebot.TeleBot(token, threaded=True, num_threads=10, parse_mode='HTML', exception_handler = ExHandler())
used_files = []
'''
nekosas = {
540255407: (16, 4),
738931917: (17, 2),
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
(11,3)
]

SERVICE_CHATID = -1001694727085
NEKOSLAVIA_CHATID = -1001268892138
ME_CHATID = 738931917
TIMESTAMP = 3*3600
USER_BOT = 6557597614

APP_URL = f'https://nekocringebot.onrender.com/{token}'
app = Flask(__name__)
bot.remove_webhook()
bot.set_webhook(url=APP_URL, allowed_updates=['message', 'callback_query', 'message_reaction', 'message_reaction_count'])

react_id = []

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

@bot.message_handler(commands=["start"])
def msg_start(message):
    return

@bot.message_handler(commands=["test"])
def msg_test(message):
    jobday()

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
        if message.reply_to_message is None or (message.reply_to_message.text is None and message.reply_to_message.caption is None):
            bot.send_message(message.chat.id, 'Ответом на текст еблан',reply_to_message_id=message.message_id)
            return
        with Image.open('necoarc.png') as img:
            draw = ImageDraw.Draw(img)
            if message.reply_to_message.text is not None:
                text = message.reply_to_message.text
            else:
                text = message.reply_to_message.caption
            draw_text_rectangle(draw, text, 220, 106, 336, 80)
            bot.add_sticker_to_set(user_id=738931917,name='necoarc_by_NekocringeBot',emojis='🫵',png_sticker=send_pil(img))
            sset = bot.get_sticker_set('necoarc_by_NekocringeBot')
            bot.send_sticker(message.chat.id, sset.stickers[-1].file_id)

@bot.message_handler(commands=["cube"])
def msg_cube(message):
        print('принято')
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
            "target": (None,1),
            "MAX_FILE_SIZE": (None,1073741824),
            "image[]": ('result.png',bio.getvalue()),
            "speed": (None,"ufast"),
            "bg_color": (None,"000000"),
            "direction": (None,direct)
        }
        with requests.Session() as s:
            p = s.get("https://en.bloggif.com/cube-3d")
            soup = BeautifulSoup(p.text, 'lxml')
            tkn = soup.find('form')
            linkfrm = "https://en.bloggif.com" + tkn['action']
            p = s.post(linkfrm, files=dat)
            print(p)
            soup = BeautifulSoup(p.text, 'lxml')
            img = soup.find('a', class_='button gray-button')
            linkgif = "https://en.bloggif.com" + img['href']
            p = s.get(linkgif)
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
        if message.reply_to_message is not None and message.reply_to_message.from_user.id == 6964908043:
            bot.send_message(message.chat.id, 'Хохла спросить забыли',reply_to_message_id=message.message_id)
        elif message.chat.id == message.from_user.id:
            bot.send_message(NEKOSLAVIA_CHATID, f'Кто-то высрал: {txt}')
        elif '@all' in low:
            slavoneki = [5417937009,460507186,783003689,540255407,523497602,503671007,448214297,729883976,738931917]
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

@bot.message_handler(func=lambda message: True, content_types=['photo','text'])
def msg_text(message):
    if message.chat.id == -1001694727085 and message.photo is not None:
        bot.send_message(message.chat.id,str(message.photo[-1].file_id) + ' ' + str(message.photo[-1].file_size) + ' ' + bot.get_file_url(message.photo[-1].file_id), reply_to_message_id=message.message_id)
    elif message.text is not None:
        handle_text(message, message.text)
    elif message.caption is not None:
        handle_text(message, message.caption)

@bot.message_handler(func=lambda message: True, content_types=['new_chat_title'])
def msg_title(message):
    bot.send_message(message.chat.id, 'Верни бля',reply_to_message_id=message.message_id)

@bot.message_reaction_handler()
def msg_reaction(event):
    if event.message_id in react_id:
        bot.delete_message(chat_id=event.chat.id, message_id=event.message_id)
        chel = html.escape(event.user.full_name, quote = True)
        idk = event.user.id
        bot.send_message(event.chat.id, f'Сегодня с <a href="tg://user?id={idk}">{chel}</a> произойдёт нечто хорошее ✨💅')

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
        bot.send_photo(NEKOSLAVIA_CHATID,photo = bio)
        return '!', 200

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
    bot.send_sticker(SERVICE_CHATID, 'CAACAgIAAxkBAAEE3Nhikp10A0x2mXRExbnjP1Rm3m4jvAACpxAAAntFWEgwuu0ea7AOsSQE')
    response = g4f.ChatCompletion.create(
        model="gpt-4o",
        messages=[
        {"role": "system", "content": 'Некославия это крайне развитая страна, граждан которой называют некославы, а мудрого правителя некокинг, её девиз это "Славься Некославия!". Прорывом в генной инженерии стало скрещивание кошек с людьми, в результате чего получились некодевочки и некомальчики, которых очень любят некославы. Некодевочки и некомальчики в рамках космической программы Некославии колонизировали Марс и теперь живут там. Самый популярный энергетик в Некославии называется "розовый монстр". В Некославии используют некомобили - новый вид транспорта, который во всём превосходит обычные машины'},
        {"role": "user", "content": "Напиши короткое необычное пожелание доброго утра для граждан Некославии"}
        ],
    )
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
        bot.send_voice(SERVICE_CHATID, bio)

def jobhour():
    r = random.randint(1,100)
    cur = datetime.fromtimestamp(time.time() + TIMESTAMP)
    if r == 42 and cur.hour > 8:
        m = bot.send_photo(NEKOSLAVIA_CHATID, photo='AgACAgIAAx0CZQN7rQABBT9sZgdSddI0o6HbVCoyAepLzAJbTV8AAvLXMRv8KkBIe66zumUTwqwBAAMCAAN4AAM0BA')
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
    t = Thread(target=updater)
    t.start()
    bot.send_message(ME_CHATID, 'Запущено')
    app.run(host='0.0.0.0',port=80, threaded = True)
