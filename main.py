import asyncio
import uuid
from datetime import datetime
from pyrogram import Client, filters
from pymongo import MongoClient

# ===== BOT CONFIG (ALREADY SET) =====
BOT_TOKEN = "8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ"
API_ID = 20726200
API_HASH = "5e927fe061c2f988a843053b67f47da9"
MONGO_URI = "mongodb+srv://anik123:db_rashni2215@cluster0.vm9te27.mongodb.net/ahrtsbd"

AUTO_DELETE = 1800  # 30 minutes

# ===== BOT CLIENT =====
app = Client(
    "ahrtsbd-file-store",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ===== DATABASE =====
mongo = MongoClient(MONGO_URI)
db = mongo["ahrtsbd"]
files = db["files"]

# ===== START COMMAND =====
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    if len(message.command) == 1:
        await message.reply_text(
            "👋 **Welcome to AHRTSBD File Store**\n\n"
            "📤 Send me any file and get a secure download link.\n"
            "⏳ File auto deletes after 30 minutes."
        )
        return

    token = message.command[1]
    data = files.find_one({"token": token})

    if not data:
        await message.reply_text("❌ **Link expired or invalid.**")
        return

    sent = await message.reply_cached_media(data["file_id"])

    await asyncio.sleep(AUTO_DELETE)

    try:
        await sent.delete()
    except:
        pass

    files.delete_one({"token": token})

# ===== FILE HANDLER =====
@app.on_message(filters.private & filters.media)
async def handle_file(client, message):
    token = str(uuid.uuid4())

    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.photo:
        file_id = message.photo.file_id
    else:
        return

    files.insert_one({
        "token": token,
        "file_id": file_id,
        "time": datetime.utcnow()
    })

    bot_username = (await client.get_me()).username
    link = f"https://t.me/{bot_username}?start={token}"

    await message.reply_text(
        f"✅ **File Stored Successfully!**\n\n"
        f"🔗 **Download Link:**\n{link}\n\n"
        f"🕒 Auto delete after 30 minutes."
    )

app.run()
