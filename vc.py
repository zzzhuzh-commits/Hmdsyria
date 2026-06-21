from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pyrogram import Client
import config

app = Client(
    "vc-ultra",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

vc = PyTgCalls(app)

async def play(chat_id, url):
    await vc.join_group_call(chat_id, AudioPiped(url))

async def stop(chat_id):
    await vc.leave_group_call(chat_id)
