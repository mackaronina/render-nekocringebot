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

monsters_db = {"Zero Sugar Monster Energy": "https://web-assests.monsterenergy.com/mnst/8a27ef6b-8c73-47b6-8321-122db0926f0a.png",
"The Original Green Monster Energy": "https://web-assests.monsterenergy.com/mnst/8edc1d77-167b-464d-b57b-2aa6bab48a0c.png",
"Zero Ultra a.k.a. The White Monster": "https://web-assests.monsterenergy.com/mnst/3214808a-90a7-474d-9cc5-7f495eae23de.png",
"Java Monster Salted Caramel": "https://web-assests.monsterenergy.com/mnst/ac2c0d32-97c7-4c48-8cca-269e43f22a42.png",
"Juice Monster Mango Loco": "https://web-assests.monsterenergy.com/mnst/d9229f7a-7d32-4ad9-8ee8-df40b58cde7b.png",
"Rehab Monster Tea & Lemonade": "https://web-assests.monsterenergy.com/mnst/cd27850b-d417-4b3c-bd56-6a7d877c42c1.png",
"Zero-Sugar Ultra Fantasy Ruby Red": "https://web-assests.monsterenergy.com/mnst/38ddb70e-3f4e-4010-ad90-b56a27488c1f.png",
"Java Monster Irish Crème": "https://web-assests.monsterenergy.com/mnst/6453e22e-627b-4ebc-9c3f-63a46d39d748.png",
"The Original Lo-Carb Monster Energy": "https://web-assests.monsterenergy.com/mnst/01a055b8-1d59-4292-ae91-5e726aa8c807.png",
"Monster Energy Nitro Super Dry": "https://web-assests.monsterenergy.com/mnst/4b6857e5-1f36-445e-bfdb-b8c73829b628.png",
"Monster Energy Nitro Cosmic Peach": "https://web-assests.monsterenergy.com/mnst/5b348c1b-f347-4b2e-ae49-fcdc3d743228.png",
"Monster Energy Reserve Peaches n’ Crème": "https://web-assests.monsterenergy.com/mnst/2012ee00-b3fa-43d2-87b5-10239b908324.png",
"Monster Energy Reserve Kiwi Strawberry": "https://web-assests.monsterenergy.com/mnst/04ecd95f-dc1b-468d-9298-83ff4a7a30ac.png",
"Monster Energy Reserve White Pineapple": "https://web-assests.monsterenergy.com/mnst/ca3e18bd-d6b4-4d6a-84df-303be714946d.png",
"Monster Energy Reserve Watermelon": "https://web-assests.monsterenergy.com/mnst/6f0d43d2-7ccc-4fa6-9452-cd187e834852.png",
"Monster Energy Reserve Orange Dreamsicle": "https://web-assests.monsterenergy.com/mnst/1f958231-848d-47b9-bc1a-07ec623d3046.png",
"Monster Energy Assault": "https://web-assests.monsterenergy.com/mnst/fd697b2e-83ef-4799-95af-633bbecbbf21.png",
"The Original Monster Energy Super-Premium Import": "https://web-assests.monsterenergy.com/mnst/6975b45a-9717-48d1-977c-59fbb1df1bf1.png",
"Zero-Sugar Ultra Peachy Keen": "https://web-assests.monsterenergy.com/mnst/df8886f5-fe3b-476a-a69f-3f1c8b8eddf4.png",
"Zero-Sugar Ultra Watermelon": "https://web-assests.monsterenergy.com/mnst/c08b0c3d-4579-4be6-9874-7cd7cd5b04f7.png",
"Zero-Sugar Ultra Gold": "https://web-assests.monsterenergy.com/mnst/ddf619ca-4987-4c91-8e3d-f74d954e9833.png",
"Zero-Sugar Ultra Sunrise": "https://web-assests.monsterenergy.com/mnst/07c0bc1e-a6a3-4c5c-99f7-85a4cdbfb6ac.png",
"Zero-Sugar Ultra Rosá": "https://web-assests.monsterenergy.com/mnst/18f8da16-4eb3-46f2-86c1-168a2c1f5769.png",
"Zero-Sugar Ultra Violet a.k.a. The Purple Monster": "https://web-assests.monsterenergy.com/mnst/67ad7b90-d9ac-4d5a-a199-4c9da9a9cbf0.png",
"Zero-Sugar Ultra Red": "https://web-assests.monsterenergy.com/mnst/b36711fc-af48-4df0-880a-8d6a60bbda69.png",
"Zero-Sugar Ultra Blue a.k.a. The Blue Monster": "https://web-assests.monsterenergy.com/mnst/5e08a00c-eb85-4b33-9b36-cd32961a9ba9.png",
"Zero-Sugar Ultra Black": "https://web-assests.monsterenergy.com/mnst/4dec66eb-3fae-4fa4-8e94-f93f520129e9.png",
"Zero-Sugar Ultra Strawberry Dreams": "https://web-assests.monsterenergy.com/mnst/06996280-74a7-417b-84d1-939ce255eef1.png",
"Java Monster Mean Bean": "https://web-assests.monsterenergy.com/mnst/1ab2af13-698a-4cbd-b066-1b97b0e53370.png",
"Java Monster Loca Moca": "https://web-assests.monsterenergy.com/mnst/b956c776-0858-4b8f-84e6-93c5c6f18f52.png",
"Café Latte": "https://web-assests.monsterenergy.com/mnst/9e69f70f-8efa-4a95-999d-9b6a9b0e37e8.png",
"Java Monster Triple Shot French Vanilla": "https://web-assests.monsterenergy.com/mnst/2644974f-6dcb-49d9-806b-56e19d6e544f.png",
"Java Monster Triple Shot Mocha": "https://web-assests.monsterenergy.com/mnst/8bf162c8-475c-4835-9f75-66815e3ed9d5.png",
"Juice Monster Aussie Style Lemonade": "https://web-assests.monsterenergy.com/mnst/7a358faa-5491-45a5-b1d1-b268ac6b445e.png",
"Juice Monster Khaotic": "https://web-assests.monsterenergy.com/mnst/8eb7d1bf-1231-4b74-9362-b93f39a33654.png",
"Juice Monster Pacific Punch": "https://web-assests.monsterenergy.com/mnst/077196b8-3934-4aca-89c4-4826a4047c7c.png",
"Juice Monster Pipeline Punch": "https://web-assests.monsterenergy.com/mnst/2a7484ad-e9d6-4972-b5ff-46269bb78f35.png",
"Juice Monster Rio Punch": "https://web-assests.monsterenergy.com/mnst/768f6319-c84c-4093-a805-0bb4eeb1cbc2.png",
"Rehab Monster Peach Tea": "https://web-assests.monsterenergy.com/mnst/7702ee33-b315-42fa-9337-1de7594d2dcc.png",
"Rehab Monster Wild Berry": "https://web-assests.monsterenergy.com/mnst/e9067c75-0881-46be-b8b5-d7e363d7532b.png",
"Rehab Monster Green Tea": "https://web-assests.monsterenergy.com/mnst/f63bfe53-d0b2-4c1e-8b48-19a5cfa528ae.png",
"Rehab Monster Strawberry Lemonade": "https://web-assests.monsterenergy.com/mnst/4139d011-1a61-4a13-baf8-7ac35df58808.png",
"Rehab Monster Watermelon": "https://web-assests.monsterenergy.com/mnst/0c0be2b5-f78b-4437-99c1-3f2bbc306e99.png",
"Das Original Green Monster Energy": "https://web-assests.monsterenergy.com/mnst/684a8881-6428-4db9-b031-cec29184deba.png",
"Ultra a.k.a. Das Weiße Monster": "https://web-assests.monsterenergy.com/mnst/24254111-11e1-4b57-80d5-75facf8c97c6.png",
"Lewis Hamilton Zero Sugar": "https://web-assests.monsterenergy.com/mnst/1394f712-7501-4b4a-b1c6-d07d66681adb.png",
"Zero Zucker Ultra Gold": "https://web-assests.monsterenergy.com/mnst/971cd2ed-47d0-4bbe-8e68-8236cf824af2.png",
"Ultra Fiesta Mango": "https://web-assests.monsterenergy.com/mnst/9e5a4d56-6861-4c4c-ad40-a60601478778.png",
"Ultra Paradise": "https://web-assests.monsterenergy.com/mnst/097fd2ef-58f2-41a8-9529-61e6ead14f26.png",
"Juiced Monster Aussie Lemonade": "https://web-assests.monsterenergy.com/mnst/a13dce97-7d59-4289-a298-f828cd320731.png",
"Zero-Sugar Ultra Fiesta Mango": "https://web-assests.monsterenergy.com/mnst/9682f578-2c19-446d-aefb-be916fe1125d.png",
"Super Dry": "https://web-assests.monsterenergy.com/mnst/238b1f70-10fe-48e1-9313-3fb6ed2b2e54.png",
"Zero-Sugar Ultra Paradise": "https://web-assests.monsterenergy.com/mnst/951c8199-a506-47b2-b11f-ea33e4b30dc9.png",
"Zero-Sugar Peachy Keen": "https://web-assests.monsterenergy.com/mnst/f438ccb6-0ce1-472f-b542-0655685bc15a.png",
"Originalni zeleni Monster Energy": "https://web-assests.monsterenergy.com/mnst/7e10162e-6930-476e-ad2c-2921b4a56882.png",
"VR46 aka. The Doctor Monster Energy": "https://web-assests.monsterenergy.com/mnst/bb9bf75a-d0b1-4cd9-8f06-bb11438c5c43.png",
"Ultra a.k.a. The White Monster": "https://web-assests.monsterenergy.com/mnst/858123d3-86f5-4652-a794-0d97d46162d8.png",
"Monster Monarch": "https://web-assests.monsterenergy.com/mnst/909da208-563b-4dba-96ae-a00564ae403c.png",
"Juiced Monster Mixxd Punch": "https://web-assests.monsterenergy.com/mnst/4c6a6241-2f1f-48fa-89b0-d4edc6beab51.png",
"L'originale : la Monster Energy verte": "https://web-assests.monsterenergy.com/mnst/b672cf95-54b1-4984-a036-5e3cb08c85fd.png",
"ULTRA FIESTA": "https://web-assests.monsterenergy.com/mnst/73d5cd46-9821-4513-bb9d-ff7b4411589d.png",
"Juiced Aussie Lemonade": "https://web-assests.monsterenergy.com/mnst/7f733e9c-416d-4245-85c8-400739ce6bcb.png",
"L'Originale Monster Energy avec zéro sucre": "https://web-assests.monsterenergy.com/mnst/17fc3c6d-66fb-4e47-939e-fc392255520d.png",
"": "https://web-assests.monsterenergy.com/mnst/78cdac42-e319-47a1-963c-9994a468e158.png",
"Peachy Keen": "https://web-assests.monsterenergy.com/mnst/12ebb880-aa27-4aa3-bde8-53d7e79344bc.png",
"Bad Apple": "https://web-assests.monsterenergy.com/mnst/df480dc6-3656-473b-af64-61ea56c6f249.png",
"Оригиналният Зелен Monster Energy": "https://web-assests.monsterenergy.com/mnst/7aaad2bd-15b7-4837-a602-c92dad671c2e.png",
"Juiced Monster Monarch": "https://web-assests.monsterenergy.com/mnst/6658ee55-a54c-42e4-bfb0-fcc35ebfdacd.png",
"Оригиналният Absolutely Zero Monster Energy": "https://web-assests.monsterenergy.com/mnst/b655f649-9039-4a23-a219-e687d3b7d0f9.png",
"Juiced Monster Khaotic": "https://web-assests.monsterenergy.com/mnst/ef202558-8dd3-430b-b4a8-e0b651d16367.png",
"The Original Lo-Cal Monster Energy": "https://web-assests.monsterenergy.com/mnst/912f010a-3189-4dbe-8622-4d7b1e51f841.png",
"MONSTER ENERGY RES": "https://web-assests.monsterenergy.com/mnst/7097a99c-a7fb-45fc-abdc-a3059c895f2d.png",
"Zero-Sugar Ultra Fiesta": "https://web-assests.monsterenergy.com/mnst/4e07be66-f9fd-409b-a916-3954173d3284.png",
"Punch Monster Papillon": "https://web-assests.monsterenergy.com/mnst/75a91f9d-00f9-4ef9-8960-8657200870f7.png",
"Rehab Monster Wild Berry Tea": "https://web-assests.monsterenergy.com/mnst/f3d281dd-be82-4d88-9009-63b93ba2f860.png",
"Monster Rehab Iced Tea & Lemonade": "https://web-assests.monsterenergy.com/mnst/70171095-b132-4ed7-b1c4-95299831ba04.png",
"Juiced Monster Pipeline Punch": "https://web-assests.monsterenergy.com/mnst/e603c9a3-3eeb-4063-95b6-2ea20c2ea0d7.png",
"Juiced Monster Μixxd Punch": "https://web-assests.monsterenergy.com/mnst/7ad5b37e-c272-41e5-8520-413df02d9890.png",
"Juiced Monarch": "https://web-assests.monsterenergy.com/mnst/56fcc7a2-70ba-4680-bafc-139cdaa08d66.png",
"Originální zelený Monster Energy": "https://web-assests.monsterenergy.com/mnst/ddc812bb-d65a-48f3-99b1-52aee9fbb02c.png",
"Ultra Rosá bez cukru": "https://web-assests.monsterenergy.com/mnst/55c6b119-47aa-402b-91f0-2cc065473197.png",
"Ultra a.k.a. bílý Monster": "https://web-assests.monsterenergy.com/mnst/80e7a806-f1f2-491b-936f-4e5209572784.png",
"Absolutely Zero Monster Energy": "https://web-assests.monsterenergy.com/mnst/6b1af42a-bc8e-4b87-bc63-0076450167d7.png",
"Ultra Fiesta bez cukru": "https://web-assests.monsterenergy.com/mnst/d22873ca-6ddb-41be-ac27-8d7ca2f5f296.png",
"Ultra Paradise bez cukru": "https://web-assests.monsterenergy.com/mnst/fd83cfb4-ad63-40df-a48d-9041555eb5ee.png",
"Ultra Watermelon bez cukru": "https://web-assests.monsterenergy.com/mnst/eb31b907-7ba5-4221-a15e-1245e03e5d66.png",
"Ultra Golden Pineapple bez cukru   ": "https://web-assests.monsterenergy.com/mnst/38b35e8f-92a9-441f-a119-66cc2ad0a4ce.png",
"Juiced Monster Bad Apple": "https://web-assests.monsterenergy.com/mnst/c1e36b73-5531-4952-9edd-bfeda25b323d.png",
"Zero Zucker Ultra Peachy Keen": "https://web-assests.monsterenergy.com/mnst/9a2b193a-5018-407a-b28d-b9f748ae26b4.png",
"Das Original Zero Zucker Monster Energy": "https://web-assests.monsterenergy.com/mnst/fa81f857-4f7a-4e4f-be31-f9374b207b06.png",
"Monster Reserve Orange Dreamsicle": "https://web-assests.monsterenergy.com/mnst/352a8171-b96f-437b-9001-dcf5c7c0cd35.png",
"VR46 alias Der Doctor Monster Energy": "https://web-assests.monsterenergy.com/mnst/8a0d8756-37c6-49cf-ab3b-e2da3ac0a0f7.png",
"Zero Zucker Ultra Rosá": "https://web-assests.monsterenergy.com/mnst/43a3c032-5f2b-4ff5-838f-9a8be9a7657c.png",
"Zero Zucker Ultra Fiesta": "https://web-assests.monsterenergy.com/mnst/7944f745-31ad-46ad-9dbb-36189658c00b.png",
"Zero Zucker Ultra Paradise": "https://web-assests.monsterenergy.com/mnst/3d2c4035-57a9-4747-b0ba-6b2efc5a3ba0.png",
"Zero Zucker Ultra Watermelon": "https://web-assests.monsterenergy.com/mnst/a4cef052-96fb-4cea-a0d7-09d31f86c992.png",
"Monster Rehab Peach Iced Tea": "https://web-assests.monsterenergy.com/mnst/9ae13382-e202-4178-ad02-7cdea40157fa.png",
"Den originale - Monster Energy": "https://web-assests.monsterenergy.com/mnst/37402668-6ac8-4edb-9ad0-3e684ff74962.png",
"Ultra White": "https://web-assests.monsterenergy.com/mnst/ad05834e-2a09-4d0f-937e-3c1d529f2750.png",
"Juiced Bad Apple": "https://web-assests.monsterenergy.com/mnst/77b35213-4c85-4509-ba80-af3cd668d079.png",
"Roheline Originaal Monster Energy": "https://web-assests.monsterenergy.com/mnst/46e43284-2336-4e86-8454-1b76c5d5485a.png",
"Ultra ehk Valge Monster": "https://web-assests.monsterenergy.com/mnst/a5c2e491-5a54-4df0-849b-92946d60dae7.png",
"Suhkruvaba Ultra Paradise": "https://web-assests.monsterenergy.com/mnst/61c9bd6b-152c-4514-b14e-6b929008bb87.png",
"Suhkruvaba Ultra Watermelon": "https://web-assests.monsterenergy.com/mnst/e68a10a3-3dab-4d71-9a24-ecf950a3c11b.png",
"Juiced Monster Mango Loco": "https://web-assests.monsterenergy.com/mnst/1d72d050-6400-48bc-80ba-59186df776db.png",
"VR46 ehk The Doctor Monster Energy": "https://web-assests.monsterenergy.com/mnst/655e8008-e913-47dd-8649-58ba0e3031c8.png",
"LH44 Monster Energy": "https://web-assests.monsterenergy.com/mnst/2fe9e84a-e741-4bb3-b8e3-0a13d0272970.png",
"Suhkruvaba Ultra Fiesta": "https://web-assests.monsterenergy.com/mnst/94544c40-39a6-4dee-bd53-b7abed9f09fa.png",
"Suhkruvaba Ultra Violet ehk Lilla Monster": "https://web-assests.monsterenergy.com/mnst/be574aea-af13-449e-8781-465c7b11a152.png",
"Suhkruvaba Ultra Golden Pineapple": "https://web-assests.monsterenergy.com/mnst/a3bc08f7-1674-4d54-ba52-361f8f57865f.png",
"Suhkruvaba Ultra Rosá": "https://web-assests.monsterenergy.com/mnst/66d888f2-5e9c-41de-bc7c-0e917556ec7d.png",
"Juiced Monster Pacific Punch": "https://web-assests.monsterenergy.com/mnst/e3fcb373-4d69-4f63-a8e7-186015475c5c.png",
"Zero Ultra White": "https://web-assests.monsterenergy.com/mnst/784c7831-f799-4679-82a7-5056c47b448d.png",
"Zero Ultra Fiesta Mango": "https://web-assests.monsterenergy.com/mnst/55e8cd2d-fc03-4e7f-b724-81d7d3007077.png",
"Zero Ultra Gold": "https://web-assests.monsterenergy.com/mnst/fdeda3e0-28b5-4ceb-9849-da63b19f274a.png",
"Monster Mule": "https://web-assests.monsterenergy.com/mnst/8c72c1ba-19e9-4c60-b327-a5448b868562.png",
"Monster Reserve Watermelon": "https://web-assests.monsterenergy.com/mnst/e96fc727-ad05-4321-9d75-1594d33955a2.png",
"Zero Ultra Paradise": "https://web-assests.monsterenergy.com/mnst/8f517174-79bc-4677-a2a1-44dd8884e555.png",
"Zero Ultra Watermelon": "https://web-assests.monsterenergy.com/mnst/c25be202-0437-4ade-924a-bb29984824ca.png",
"Zero Ultra Red": "https://web-assests.monsterenergy.com/mnst/8df27b27-f25b-4da9-971d-f394c312e55e.png",
"Monster Ultra Rosá": "https://web-assests.monsterenergy.com/mnst/265f8041-ed4d-4850-b9c9-d829c21b94b5.png",
"Monster Ultra Peachy Keen ": "https://web-assests.monsterenergy.com/mnst/83b26e30-0561-451f-8e72-3f863527660d.png",
"Juiced Monster Ripper": "https://web-assests.monsterenergy.com/mnst/7f94b723-d78b-4d5b-bff2-4b51b97ccde7.png",
"Monster Juiced Bad Apple": "https://web-assests.monsterenergy.com/mnst/64fda345-6bd7-4e1b-8de5-228b29acdcc7.png",
"Juiced Monster Mixxd": "https://web-assests.monsterenergy.com/mnst/ef1074d8-b8f9-40e7-ac08-5a9e040b9b8f.png",
"Originalni Zero Sugar Monster Energy": "https://web-assests.monsterenergy.com/mnst/2c79699c-a84e-43dd-93aa-a2c19fdcc928.png",
"Az Eredeti Zöld Monster Energy": "https://web-assests.monsterenergy.com/mnst/9be49781-2549-478f-8bf4-3f23c992f327.png",
"Zéró Cukor Ultra azaz a Fehér Monster": "https://web-assests.monsterenergy.com/mnst/80dd6723-1f4c-4702-bdcd-d1f4af39dc50.png",
"Monster Rehab Barackos Jeges Tea": "https://web-assests.monsterenergy.com/mnst/b65be493-c551-40c7-9a37-18a1923ab14a.png",
"VR46 azaz A Doktor Monster Energy": "https://web-assests.monsterenergy.com/mnst/369ff79a-319a-4697-8344-4fa1b8f816af.png",
"Zéró-Cukor Ultra Watermelon": "https://web-assests.monsterenergy.com/mnst/c0b9b5f0-68d0-40e9-988a-04d9d180c321.png",
"Zéró Cukor - Ultra Fiesta Mango": "https://web-assests.monsterenergy.com/mnst/009ff8aa-b069-4f65-a595-53b4815d940a.png",
"Zéró Cukor - Ultra Paradise": "https://web-assests.monsterenergy.com/mnst/620f0ae7-a9ad-4bcf-a67c-eef678d3ce89.png",
"Zéró Cukor Ultra Gold Pineapple": "https://web-assests.monsterenergy.com/mnst/43f681df-42dd-4b2e-875b-1540f5f9e080.png",
"Zéró Cukor Ultra Rosá": "https://web-assests.monsterenergy.com/mnst/b95e59df-524d-4514-9f3a-9c61cb96c1a1.png",
"Juiced Monster Aussie Style Lemonade": "https://web-assests.monsterenergy.com/mnst/70181459-6c8e-45f4-8e50-24c453df72f2.png",
"Monster Rehab Jeges Tea & Limonádé": "https://web-assests.monsterenergy.com/mnst/5368741f-bf01-4de4-bfb2-e580fecb4215.png",
"Monster Superfuel Subzero": "https://web-assests.monsterenergy.com/mnst/5fe76879-3a13-4dbc-b2ef-6e5b033ad7b2.png",
"Monster Superfuel Mean Green": "https://web-assests.monsterenergy.com/mnst/d41b2fa9-957f-4d99-ad33-10a462e374f3.png",
"Monster Ultra White senza zucchero": "https://web-assests.monsterenergy.com/mnst/353ee823-5e22-46aa-82d5-3d8338e4b5be.png",
"Monster Energy Absolutely Zero": "https://web-assests.monsterenergy.com/mnst/a466a0d1-d957-400a-a888-2edb847af5a5.png",
"The Doctor": "https://web-assests.monsterenergy.com/mnst/376a0b93-4ade-4952-a3b5-958e24ea3aec.png",
"Monster Ultra Red senza zucchero": "https://web-assests.monsterenergy.com/mnst/74940027-8189-4277-90d2-c371ddb15168.png",
"Monster Ultra Paradise senza zucchero": "https://web-assests.monsterenergy.com/mnst/9b12b270-b28d-49f4-92c7-19e71b0b9fa8.png",
"Monster Ultra Golden Pineapple senza zucchero": "https://web-assests.monsterenergy.com/mnst/81017960-091a-4d26-8b6e-c43bf7509235.png",
"Monster Energy Rehab Tea + Limonata": "https://web-assests.monsterenergy.com/mnst/34259d6a-1d13-4c13-9b25-ac6be2971ce2.png",
"モンスターエナジー": "https://web-assests.monsterenergy.com/mnst/1186276a-a7e1-4b0f-8658-b62aa3fb4cfe.png",
"モンスター ウルトラ": "https://web-assests.monsterenergy.com/mnst/8f5bfc87-8516-46df-8c94-bdd0cec8fcf0.png",
"モンスター マンゴーロコ": "https://web-assests.monsterenergy.com/mnst/9f8bf29c-7d93-40df-977b-7dbb6639e8f7.png",
"モンスター パイプラインパンチ": "https://web-assests.monsterenergy.com/mnst/c910c515-0eac-4388-97a7-c4c79c526d30.png",
"モンスターエナジー ゼロシュガー": "https://web-assests.monsterenergy.com/mnst/36091676-bb8f-4396-990d-224910a616d0.png",
"モンスターエナジー 缶500ml": "https://web-assests.monsterenergy.com/mnst/6407593c-559c-41b7-93a2-a272f48370c1.png",
"モンスター ウルトラバイオレット": "https://web-assests.monsterenergy.com/mnst/b48c6ceb-033b-493a-b480-dc43167861bd.png",
"モンスター パピヨン": "https://web-assests.monsterenergy.com/mnst/f926cbe3-69fb-4873-91ba-3338a5a6c8ef.png",
"モンスターエナジー M3": "https://web-assests.monsterenergy.com/mnst/4b001ad9-703b-4c28-b1a3-64ea13289e57.png",
"モンスターエナジーボトル缶500ml": "https://web-assests.monsterenergy.com/mnst/dcfd40ca-5e82-453f-b57b-11ddc78cf902.png",
"モンスター スーパーコーラ": "https://web-assests.monsterenergy.com/mnst/9052bf41-7b24-4ad0-abf8-6344de772798.png",
"モンスター ウルトラパラダイス": "https://web-assests.monsterenergy.com/mnst/245513bb-a178-4a33-adc1-de37d31481a6.png",
"Zero-Sugar Ultra / Ultra a.k.a. De Witte Monster": "https://web-assests.monsterenergy.com/mnst/42dbcfee-7b00-44a7-af51-d2cfcb168ad2.png",
"Den originale - Green Monster Energy": "https://web-assests.monsterenergy.com/mnst/ba48aeb2-b648-4133-b657-c4dafee562a1.png",
"Ultra Fiesta Uten Sukker": "https://web-assests.monsterenergy.com/mnst/fe547c65-de49-4bb2-858e-0aa74bb2e395.png",
"Ultra Gold Uten Sukker": "https://web-assests.monsterenergy.com/mnst/e31d174e-ec80-4618-aa03-09b56bf54835.png",
"Ultra Paradise Uten Sukker": "https://web-assests.monsterenergy.com/mnst/517a2ba4-a942-428b-8ff4-def3eda231d1.png",
"Ultra Watermelon Uten Sukker": "https://web-assests.monsterenergy.com/mnst/a9006481-47a1-4cdb-b4c1-2c530aa9743d.png",
"Ultra a.k.a. Hvit Monster Uten Sukker": "https://web-assests.monsterenergy.com/mnst/cebc6b74-5167-4e99-8a51-490ce8e564e9.png",
"Ultra Rosá Uten Sukker": "https://web-assests.monsterenergy.com/mnst/abdd40dc-0f96-4a69-9f0e-3c1bb2959afa.png",
"Ultra Black Uten Sukker    ": "https://web-assests.monsterenergy.com/mnst/811d4b40-0c2b-48d2-9b12-4dd2be000980.png",
"Ultra Peachy Keen Uten Sukker": "https://web-assests.monsterenergy.com/mnst/7187cd16-688d-49e5-831e-13bbc16361d3.png",
"Monster Green Zero Cukru": "https://web-assests.monsterenergy.com/mnst/548ed3f8-24d3-4518-a6c8-0c6ca1ae6d5c.png",
"Ultra Peachy Keen Bez Cukru    ": "https://web-assests.monsterenergy.com/mnst/4a0d9410-d76a-491c-b7ab-9948bc30484b.png",
"Oryginalny zielony Monster Energy": "https://web-assests.monsterenergy.com/mnst/6a18e0a7-d8f2-46a6-9207-1419e5304bb7.png",
"VR46, czyli Monster Energy The Doctor": "https://web-assests.monsterenergy.com/mnst/52f29a9d-9c90-4e01-8a64-2ef8b8f9db5d.png",
"Ultra, czyli Biały Monster": "https://web-assests.monsterenergy.com/mnst/e9af5647-5bcc-4c2f-b7b5-c7d6679d8528.png",
"Ultra Fiesta Mango Bez Cukru": "https://web-assests.monsterenergy.com/mnst/4bc73a8d-fa38-4a90-878d-970f3266bd82.png",
"Ultra Violet Bez Cukru, czyli Fioletowy Monster": "https://web-assests.monsterenergy.com/mnst/456e8601-a8d5-47cd-b93c-77827aa37358.png",
"Ultra Strawberry Dreams Bez Cukru  ": "https://web-assests.monsterenergy.com/mnst/089dfdf5-bc04-41e4-92db-73a4178827e5.png",
"Ultra Black Bez Cukru": "https://web-assests.monsterenergy.com/mnst/562abb40-01df-4079-9eed-d58b23abe602.png",
"Monster Energy Original": "https://web-assests.monsterenergy.com/mnst/99732d67-c85d-472e-a9cd-6b6eff16e15b.png",
"Monster Energy Rehab": "https://web-assests.monsterenergy.com/mnst/6675abb3-7e95-4463-9fbe-88c4b71bd7c4.png",
"Monster Energy Original Verde": "https://web-assests.monsterenergy.com/mnst/04308394-fa8f-4c9b-865d-96c52a871dcb.png",
"Originalul Monster Energy Zero-Zahăr": "https://web-assests.monsterenergy.com/mnst/64a00617-cd2b-4f76-89da-f41f871a3584.png",
"Ultra a.k.a. Monster Alb": "https://web-assests.monsterenergy.com/mnst/95fa41b4-4e6e-4e88-b9f7-04b7b18758f4.png",
"Ultra Fiesta Mango Zero-Zahăr": "https://web-assests.monsterenergy.com/mnst/4fb1ce0d-2ca1-4ae8-b553-98f95030a15c.png",
"Ultra Paradise Zero-Zahăr": "https://web-assests.monsterenergy.com/mnst/db3a759b-caf4-46fb-aab5-fa5271021f07.png",
"Ultra Watermelon Zero Zahăr": "https://web-assests.monsterenergy.com/mnst/a7c99eaa-f988-4d68-a9af-fcf0ea331d8a.png",
"Ultra Golden Pineapple Zero-Zahăr": "https://web-assests.monsterenergy.com/mnst/439cada3-5c4c-4f01-a5fe-d65544a5f908.png",
"Original Zeleni Monster Energy": "https://web-assests.monsterenergy.com/mnst/c1baa7dc-2d63-45e3-9886-7c0a61402c53.png",
"Orginalet - Green Monster Energy": "https://web-assests.monsterenergy.com/mnst/35b0797d-fcd4-4286-b4c6-9d781d1713bb.png",
"Reserve Pineapple": "https://web-assests.monsterenergy.com/mnst/6d23c6b2-7eba-4777-a604-7e4a469f4ddf.png",
"Originalet - Zero Sugar Monster Energy": "https://web-assests.monsterenergy.com/mnst/fd97b4a1-3537-4eca-8cef-199cd0474669.png",
"Originalni Monster Energy brez sladkorja": "https://web-assests.monsterenergy.com/mnst/03ee322e-9674-40d5-83f2-761dc3267ce1.png",
"Monster Energy VR46": "https://web-assests.monsterenergy.com/mnst/0d14f3c9-e089-4c67-84c8-27cbe2a646d5.png",
"Originálny zelený Monster Energy": "https://web-assests.monsterenergy.com/mnst/4dcbabff-b26c-4019-8dbe-573ffada006d.png",
"Класичний Зелений Monster Energy": "https://web-assests.monsterenergy.com/mnst/dcb01916-4b8e-437f-a844-3b82aed25593.png",
"Ультра, a.k.a Білий Monster": "https://web-assests.monsterenergy.com/mnst/e23d3407-a2dd-42ee-87a3-0aa09f5d9aef.png",
"Juiced Monster Mucho Loco": "https://web-assests.monsterenergy.com/mnst/e8ccc4e5-7dc6-46c8-9b68-e52e05bb75c0.png",
"The Non-Alcoholic Monster Mule": "https://web-assests.monsterenergy.com/mnst/c0ab40b1-8949-4616-928a-d7e75dd0e678.png",
"The Original Absolutely Zero Monster Energy": "https://web-assests.monsterenergy.com/mnst/148a6e36-0575-435e-9932-30164ed38f3b.png",
"Juiced Monster Mariposa": "https://web-assests.monsterenergy.com/mnst/f8de4fcf-9c3b-47a7-acf1-4079e433a438.png",
"Monster Rehab Lemon": "https://web-assests.monsterenergy.com/mnst/0088a23b-7413-4ddd-802d-fa75cffdb455.png",
"Monster Rehab Peach": "https://web-assests.monsterenergy.com/mnst/0cbed87a-f054-4267-bfa5-fa680860548e.png"}

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
    bot.send_message(ME_CHATID, 'Запущено')
    app.run(host='0.0.0.0',port=80, threaded = True)
