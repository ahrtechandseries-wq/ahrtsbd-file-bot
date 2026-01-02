import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 20726200))
API_HASH = os.environ.get("API_HASH", "5e927fe061c2f988a843053b67f47da9")
BOT_TOKEN = os.environ.get("8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ")

app = Client("ahrtsbd_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- FLASK WEB SERVER (Render Fix) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "AHRTSBD is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

user_data = {}

# --- START COMMAND (Link Handling) ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.command) > 1:
        file_id = message.command[1]
        wait_msg = await message.reply_text("⏳ **ফাইলটি সার্ভার থেকে আনা হচ্ছে...**")
        
        try:
            # সরাসরি ফাইল পাঠানোর সবথেকে ভালো উপায়
            sent_file = await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=file_id,
                caption="🚀 **Shared by: AHRTSBD**\n\n⚠️ এই ফাইলটি ৩০ মিনিট পর ডিলিট হবে।"
            )
            await wait_msg.delete()

            notice = await message.reply_text(
                "✅ **ফাইল পাঠানো হয়েছে!**\n\n📌 ৩০ মিনিট পর এটি ডিলিট হবে। এখনই **Saved Messages**-এ ফরওয়ার্ড করে রাখুন।"
            )

            # ৩০ মিনিট টাইমার
            await asyncio.sleep(1800)
            await sent_file.delete()
            await notice.delete()
            
        except Exception:
            await wait_msg.edit("❌ **Error:** ফাইলটি পাওয়া যায়নি। দয়া করে আবার আপলোড করে নতুন লিঙ্ক নিন।")
    else:
        await message.reply_text("👋 স্বাগতম! ফাইল আপলোড করতে /upload লিখুন।")

# --- UPLOAD COMMAND ---
@app.on_message(filters.command("upload") & filters.private)
async def upload_init(client, message):
    user_data[message.from_user.id] = []
    await message.reply_text("📤 ফাইলটি পাঠান, শেষ হলে **✅ Finish** বাটনে ক্লিক করুন।", 
                             reply_markup=ReplyKeyboardMarkup([["✅ Finish"]], resize_keyboard=True))

@app.on_message(filters.private & ~filters.command(["start", "upload"]))
async def handle_media(client, message):
    user_id = message.from_user.id
    if message.text == "✅ Finish":
        if user_id in user_data and user_data[user_id]:
            f_id = user_data[user_id][0]
            me = await client.get_me()
            link = f"https://t.me/{me.username}?start={f_id}"
            await message.reply_text(f"✅ **আপনার লিঙ্ক:**\n`{link}`", reply_markup=ReplyKeyboardRemove())
            user_data.pop(user_id)
    elif user_id in user_data:
        media = message.document or message.video or message.photo
        if media:
            user_data[user_id].append(media.file_id)
            await message.reply_text("📂 সেভ হয়েছে! আরও পাঠান বা ফিনিশ করুন।")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    app.run()
    
