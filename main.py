from telethon.sync import TelegramClient
import time
from flask import Flask
import asyncio
import g4f
import time

g4f.debug.logging = True
g4f.debug.check_version = False

api_id = 20319557
api_hash = '1eb6e800411c9c7cbe90d39db9b7d1c3'

app = Flask(__name__)

def generate_text():
    response = g4f.ChatCompletion.create(
            model="gpt-4",
            provider=g4f.Provider.Aura,
            messages=[{'role':'user','content':'Некославия это страна, граждан которой называют некославы, а правителя некокинг. Некославия развитая страна которая колонизировала Марс. Также ученым удалось скрестить кошек с людьми и получить некодевочек и некомальчиков, которых очень любят некославы. Самый популярный энергетик в Некославии это "розовый монстр". Напиши короткое необычное пожелание доброго утра для граждан этой страны'}]
    )
    print(response)
    return response

@app.route('/')
def get_ok():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient('session_name', api_id, api_hash, loop=loop) as client:
        #client = TelegramClient('session_name', api_id, api_hash, loop=loop)
        client.start()
        m = client.send_message(-1001694727085, 'Hello! Talking to you from Telethon')
        time.sleep(0.1)
        client.delete_messages(entity=-1001694727085, message_ids=[m.id])
        return 'ok', 200

@app.route('/morning')
def get_morning():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient('session_name', api_id, api_hash, loop=loop) as client:
        client.start()
        m = client.send_message('@silero_voice_bot', generate_text())
        time.sleep(5)
        m = client.get_messages('@silero_voice_bot', ids=m.id+1)
        client.forward_messages('@NekocringeBot', m)
        #@NekocringeBot
        return 'ok', 200

@app.route('/getposts')
def get_getposts():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with TelegramClient('session_name', api_id, api_hash, loop=loop) as client:
        client.start()
        for msg in client.get_messages('@animewebmtg', limit=3):
            if '#NecoArc' in msg.text:
                try:
                    client.forward_messages('@NekocringeBot', msg)
                except:
                    pass
        return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)

