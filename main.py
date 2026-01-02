import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

# --- CONFIGURATION ---
API_ID = 20726200
API_HASH = "5e927fe061c2f988a843053b67f47da9"
BOT_TOKEN = "8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ" # এখানে টোকেন দিন

app = Client("ahrtsbd_fix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER FOR RENDER ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "AHRTSBD is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- START COMMAND (File Retrieval) ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.command) > 1:
        # লিঙ্ক থেকে ফাইল পাঠানোর সবচেয়ে নিরাপদ পদ্ধতি
        data = message.command[1]
        wait_msg = await message.reply_text("⚡ **ফাইলটি সার্ভার থেকে আনা হচ্ছে...**")
        
        try:
            # সরাসরি ফাইল পাঠানোর কমান্ড
            sent_file = await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=data,
                caption="🚀 **Shared by: AHRTSBD**\n\n⚠️ ৩০ মিনিট পর এটি ডিলিট হবে।"
            )
            await wait_msg.delete()

            notice = await message.reply_text("✅ **সফলভাবে পাঠানো হয়েছে!** এখনই ফরওয়ার্ড করে রাখুন।")

            await asyncio.sleep(1800)
            await sent_file.delete()
            await notice.delete()
        except Exception as e:
            await wait_msg.edit(f"❌ **Error:** ফাইলটি পাওয়া যায়নি। নতুন করে আপলোড করুন।")
    else:
        await message.reply_text("👋 স্বাগতম! ফাইল আপলোড করতে /upload লিখুন।")

# --- UPLOAD HANDLING ---
user_temp = {}

@app.on_message(filters.command("upload") & filters.private)
async def upload(client, message):
    user_temp[message.from_user.id] = True
    await message.reply_text("📤 আপনার ফাইলটি পাঠান।", 
                             reply_markup=ReplyKeyboardMarkup([["✅ Finish"]], resize_keyboard=True))

@app.on_message(filters.private & ~filters.command(["start", "upload"]))
async def process_upload(client, message):
    user_id = message.from_user.id
    if message.text == "✅ Finish":
        user_temp.pop(user_id, None)
        await message.reply_text("✅ আপলোড শেষ হয়েছে।", reply_markup=ReplyKeyboardRemove())
    elif user_id in user_temp:
        media = message.document or message.video or message.photo
        if media:
            bot_me = await client.get_me()
            link = f"https://t.me/{bot_me.username}?start={media.file_id}"
            await message.reply_text(f"✅ **আপনার লিঙ্ক:**\n`{link}`")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    app.run()
        
