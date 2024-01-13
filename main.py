import telebot
from telebot import types
from flask import Flask, request, send_from_directory, send_file, jsonify, render_template, url_for
from petpetgif.saveGif import save_transparent_gif
from io import BytesIO, StringIO
from PIL import Image,ImageDraw,ImageFont, ImageStat
from pkg_resources import resource_stream
from threading import Thread
import time
import schedule
import requests
from bs4 import BeautifulSoup
import random
import re
import json
import html
import math
import traceback
from datetime import datetime

time.sleep(2)
token = '6964908043:AAE0fSVJGwNKOQWAwQRH6QDfuuXZx2EQNME'
class ExHandler(telebot.ExceptionHandler):
    def handle(self, exc):
        bot.send_message(ME_CHATID, traceback.format_exc())
        return True
bot = telebot.TeleBot(token, threaded=True, num_threads=10, parse_mode='HTML', exception_handler = ExHandler())
used_files = []
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

SERVICE_CHATID = -1001694727085
NEKOSLAVIA_CHATID = -1001268892138
ME_CHATID = 738931917
TIMESTAMP = 2*3600
USER_BOT = 6557597614

APP_URL = f'https://nekocringebot.onrender.com/{token}'
app = Flask(__name__)
bot.remove_webhook()
bot.set_webhook(url=APP_URL, allowed_updates=['message',  'callback_query', 'chat_member'])

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

@bot.message_handler(commands=["start"])
def msg_start(message):
    return

@bot.message_handler(commands=["test"])
def msg_test(message):
    jobhour()

@bot.message_handler(commands=["del"])
def msg_del(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.id)

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
        print('Сообщение получено')
        low = txt.lower()
        text_for_reaction = re.sub('[^а-я]', ' ', low).split()
        if message.from_user.id in nekosas:
            args = nekosas[message.from_user.id]
            dr_day = args[0]
            dr_month = args[1]
            cur = datetime.fromtimestamp(time.time() + TIMESTAMP)
            if cur.day == dr_day and cur.month == dr_month:
                bot.send_message(message.chat.id, 'Именинника спросить забыли',reply_to_message_id=message.message_id)
                return
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
        elif 'база' in text_for_reaction:
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEJqU1krYllZmDsM70Wflt5oZ3-_DwKdAACqBoAAqgrQUv0qGwOc3lWNi8E',reply_to_message_id=message.message_id)
        elif 'кринж' in text_for_reaction:
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEJqU9krYl2-rfaY7UQB_35FDwm1FBL9wACvxoAAuorQEtk0hzsZpp1hi8E',reply_to_message_id=message.message_id)
        elif 'давид' in low:
            bot.send_message(message.chat.id, 'Давид шедевр',reply_to_message_id=message.message_id)
        elif 'негр' in low or 'нигер' in low:
            set_reaction(message.chat.id, message.id, "💅")
        elif 'сбу' in text_for_reaction:
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEKWrBlDPH3Ok1hxuoEndURzstMhckAAWYAAm8sAAIZOLlLPx0MDd1u460wBA',reply_to_message_id=message.message_id)
        elif 'порох' in text_for_reaction or 'порошенко' in text_for_reaction or 'гетьман' in text_for_reaction or 'рошен' in text_for_reaction:
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEK-splffs7OZYtr8wzINEw4lxbvwywoAACXSoAAg2JiEoB98dw3NQ3FjME',reply_to_message_id=message.message_id)
        elif 'зелебоба' in text_for_reaction or 'зелень' in text_for_reaction or 'зеленский' in text_for_reaction or 'зеленський' in text_for_reaction:
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELGOplmDc9SkF-ZnVsdNl4vhvzZEo7BQAC5SwAAkrDgEr_AVwN_RkClDQE',reply_to_message_id=message.message_id)
        elif 'некоарк' in low or 'неко арк' in low or 'neco arc' in low or 'necoarc' in low:
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELHUtlm1wm-0Fc-Ny2na6ogFAuHLC-DgAChisAAgyUiEose7WRTmRWsjQE',reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda message: True, content_types=['photo','video','text','voice'])
def msg_text(message):
    if message.chat.id == USER_BOT:
        if message.voice is not None:
            bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEE3Nhikp10A0x2mXRExbnjP1Rm3m4jvAACpxAAAntFWEgwuu0ea7AOsSQE')
            bot.send_voice(NEKOSLAVIA_CHATID, message.voice.file_id)
        elif message.video is not None and message.video.file_unique_id not in used_files:
            used_files.append(message.video.file_unique_id)
            bot.send_video(NEKOSLAVIA_CHATID, message.video.file_id)
            bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAELKbBlogXcIFNenqBZ8i47PtCi9XI-GgACdisAAs-rgUqbE4x78jgMmDQE')
    elif message.text is not None:
        handle_text(message, message.text)
    elif message.caption is not None:
        handle_text(message, message.caption)

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

def updater():
    print('Поток запущен')
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def jobday():
    with requests.Session() as s:
        s.get("https://uptimebot-7oo5.onrender.com/morning")

def jobhour():
    with requests.Session() as s:
        s.get("https://uptimebot-7oo5.onrender.com/getposts")

def jobnight():
    bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEKXtllDtEnW5DZM-V3VQpFEnzKY0CTOgACsD0AAhGtWEjUrpGNhMRheDAE')

def jobweek():
    stickers = [
    'CAACAgIAAxkBAAELHRhlmy5lZ3DjqeJcBx1gzqVwPb3gAgACyRYAAqjSgUvZ7sYejHfOlzQE',
    'CAACAgIAAxkBAAELHRplmy5qczsacTL8PVB___-SYoW2KwACNxQAAksbgEvt_JM25B-dozQE',
    'CAACAgIAAxkBAAELHRxlmy5tChW5VDyUyEXWUqfHSTSgjQACohcAArw1gUu9AtlM7MrK8DQE',
    'CAACAgIAAxkBAAELHR5lmy5wBE877qJvNoUZv2qyIK4jOQACbBUAAu4tiEs5QNHnNZ-5BzQE',
    'CAACAgIAAxkBAAELHSBlmy5zlVJNQ1kpJjzLqRJpzvq9XgACWxcAAomDiUu7YG_wPShz4zQE',
    'CAACAgIAAxkBAAELHSJlmy53dhqy1F0QGZbSQV0yWhdL8gACoBYAAgwTgUsYv06y1Bvz1DQE',
    'CAACAgIAAxkBAAELHSRlmy57tJC9YoKiyAKvL9y-oAEdiQACgxUAAuqKgUvgoYyaWs-hnTQE'
    ]
    cur = datetime.now()
    if cur.month == 10 and cur.day == 19:
        bot.send_sticker(NEKOSLAVIA_CHATID, 'CAACAgIAAxkBAAEKiXplLTbsgpfjAo5uSvlAephSFbLDzAACYz4AAnnqaUmMWJC_jc4g1zAE')
    else:
        bot.send_sticker(NEKOSLAVIA_CHATID, stickers[datetime.weekday(cur)])

if __name__ == '__main__':
    schedule.every().day.at("22:00").do(jobweek)
    schedule.every().day.at("06:00").do(jobday)
    schedule.every().day.at("23:00").do(jobnight)
    schedule.every(60).minutes.do(jobhour)
    t = Thread(target=updater)
    t.start()
    bot.send_message(ME_CHATID, 'Запущено')
    app.run(host='0.0.0.0',port=80, threaded = True)