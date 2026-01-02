import asyncio
import uuid
from datetime import datetime
from pyrogram import Client, filters
from pymongo import MongoClient
from flask import Flask
import threading

# ===== BOT CONFIG =====
BOT_TOKEN = "8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ"
API_ID = 20726200
API_HASH = "5e927fe061c2f988a843053b67f47da9"
MONGO_URI = "mongodb+srv://anik123:db_rashni2215@cluster0.vm9te27.mongodb.net/ahrtsbd"
AUTO_DELETE = 1800

# ===== DATABASE =====
mongo = MongoClient(MONGO_URI)
db = mongo["ahrtsbd"]
files = db["files"]

# ===== PYROGRAM BOT =====
app = Client(
    "ahrtsbd-file-store",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ===== FLASK KEEP ALIVE =====
web = Flask(__name__)

@web.route("/")
def home():
    return "AHRTSBD File Store Bot is Running"

def run_web():
    web.run(host="0.0.0.0", port=10000)

# ===== START COMMAND =====
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    if len(message.command) == 1:
        await message.reply_text(
            "👋 Welcome to AHRTSBD File Store\n\n"
            "Send me any file and get a download link.\n"
            "File auto deletes after 30 minutes."
        )
        return

    token = message.command[1]
    data = files.find_one({"token": token})

    if not data:
        await message.reply_text("❌ Link expired or invalid")
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
    file_id = (
        message.document.file_id if message.document else
        message.video.file_id if message.video else
        message.audio.file_id if message.audio else
        message.photo.file_id
    )

    files.insert_one({
        "token": token,
        "file_id": file_id,
        "time": datetime.utcnow()
    })

    bot_username = (await client.get_me()).username
    link = f"https://t.me/{bot_username}?start={token}"

    await message.reply_text(
        f"✅ File Stored!\n\n"
        f"🔗 {link}\n\n"
        f"⏳ Auto delete in 30 minutes"
    )

# ===== RUN BOTH =====
def run_bot():
    app.run()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
