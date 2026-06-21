from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from vc import vc
import config

app = Client(
    "vc-bot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

ydl_opts = {
    "format": "bestaudio",
    "quiet": True
}

def get_audio(query):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        video = info["entries"][0]
        return video["url"], video["title"]

# ▶️ تشغيل
@app.on_message(filters.command("تشغيل"))
async def play_music(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("❌ اكتب اسم الأغنية")

    query = " ".join(msg.command[1:])
    url, title = get_audio(query)

    try:
        await vc.join_group_call(
            msg.chat.id,
            AudioPiped(url)
        )
        await msg.reply(f"🎧 تم التشغيل:\n{title}")
    except:
        await msg.reply("⚠️ شغل Voice Chat أولاً في المجموعة")

# ⛔ إيقاف
@app.on_message(filters.command("ايقاف"))
async def stop(_, msg):
    try:
        await vc.leave_group_call(msg.chat.id)
        await msg.reply("⛔ تم الإيقاف")
    except:
        await msg.reply("❌ لا يوجد تشغيل")

# 👋 بدء
@app.on_message(filters.command("بداية"))
async def start(_, msg):
    await msg.reply("👋 بوت الميوزك العربي VC شغال 🔥")

app.run()
