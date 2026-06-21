import sys
print(sys.version)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

from vc import vc
from database import queue, state
from sudo import is_sudo
import config

app = Client(
    "vc-ultra",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

ydl = {"format": "bestaudio", "quiet": True}

def get_song(query):
    with YoutubeDL(ydl) as ydlp:
        data = ydlp.extract_info(f"ytsearch:{query}", download=False)
        v = data["entries"][0]
        return v["url"], v["title"]

# 🎛 لوحة التحكم
def panel():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▶️ تشغيل", callback_data="play"),
            InlineKeyboardButton("⏸ إيقاف مؤقت", callback_data="pause")
        ],
        [
            InlineKeyboardButton("⏭ تخطي", callback_data="skip"),
            InlineKeyboardButton("⛔ إيقاف", callback_data="stop")
        ]
    ])

# ▶️ تشغيل
@app.on_message(filters.command("تشغيل"))
async def play(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("❌ اكتب اسم الأغنية")

    url, title = get_song(" ".join(msg.command[1:]))

    queue.insert_one({
        "chat_id": msg.chat.id,
        "url": url,
        "title": title
    })

    await msg.reply(f"🎧 تم إضافة:\n{title}", reply_markup=panel())

    st = state.find_one({"chat_id": msg.chat.id})
    if not st:
        await start_next(msg.chat.id)

# ▶️ تشغيل التالي
async def start_next(chat_id):
    song = queue.find_one({"chat_id": chat_id})

    if not song:
        return

    await vc.join_group_call(chat_id, AudioPiped(song["url"]))

    state.update_one(
        {"chat_id": chat_id},
        {"$set": {"current": song}},
        upsert=True
    )

    queue.delete_one({"_id": song["_id"]})

# ⏭ تخطي
@app.on_message(filters.command("تخطي"))
async def skip(_, msg):
    await vc.leave_group_call(msg.chat.id)
    await start_next(msg.chat.id)
    await msg.reply("⏭ تم التخطي")

# ⛔ إيقاف
@app.on_message(filters.command("ايقاف"))
async def stop(_, msg):
    await vc.leave_group_call(msg.chat.id)
    state.delete_one({"chat_id": msg.chat.id})
    await msg.reply("⛔ تم الإيقاف")

# 📜 Queue
@app.on_message(filters.command("قائمة"))
async def queue_list(_, msg):
    q = queue.find({"chat_id": msg.chat.id})

    text = "📜 قائمة التشغيل:\n\n"
    for i, s in enumerate(q, 1):
        text += f"{i}- {s['title']}\n"

    await msg.reply(text or "فارغة")

# 👑 إضافة sudo
@app.on_message(filters.command("رفع"))
async def add_sudo(_, msg):
    if msg.from_user.id != config.OWNER_ID:
        return

    if not msg.reply_to_message:
        return await msg.reply("رد على المستخدم")

    user = msg.reply_to_message.from_user
    from database import sudo

    sudo.insert_one({"user_id": user.id})
    await msg.reply("👑 تم رفع المستخدم")

# 🎛 أزرار التحكم
@app.on_callback_query()
async def buttons(_, cb):
    cmd = cb.data

    if cmd == "skip":
        await vc.leave_group_call(cb.message.chat.id)
        await start_next(cb.message.chat.id)
        await cb.answer("تم التخطي")

    elif cmd == "stop":
        await vc.leave_group_call(cb.message.chat.id)
        state.delete_one({"chat_id": cb.message.chat.id})
        await cb.answer("تم الإيقاف")

# 👋 بدء
@app.on_message(filters.command("بداية"))
async def start(_, msg):
    await msg.reply("🔥 بوت VC عربي ULTRA شغال")

app.run()
