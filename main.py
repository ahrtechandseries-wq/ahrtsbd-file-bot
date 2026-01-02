import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from flask import Flask
import threading
import os

# --- CONFIGURATION ---
API_ID = 20726200
API_HASH = "5e927fe061c2f988a843053b67f47da9"
BOT_TOKEN = "আপনার_বোট_টোকেন_এখানে_দিন"

app = Client("ahrtsbd_pro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Render Port Fix
app_web = Flask(__name__)
@app_web.route('/')
def hello():
    return "AHRTSBD Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

user_data = {}

# --- START COMMAND (Link Handling & Auto Delete) ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.command) > 1:
        file_id = message.command[1]
        
        proc = await message.reply_text("⏳ **অপেক্ষা করুন...**")
        
        try:
            # ফাইল পাঠানো (Digital শব্দ বাদ দেওয়া হয়েছে)
            sent_file = await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=file_id,
                caption="🚀 **Shared by: AHRTSBD**\n\n⚠️ এই ফাইলটি ৩০ মিনিট পর ডিলিট হবে।"
            )

            await proc.delete()

            notice = await message.reply_text(
                "✅ **ফাইল সফলভাবে পাঠানো হয়েছে!**\n\n"
                "⚠️ **সতর্কবার্তা:**\n"
                "নিরাপত্তার স্বার্থে এটি **৩০ মিনিট** পর এখান থেকে ডিলিট হবে।\n\n"
                "📌 **তাই ফাইলটি এখনই আপনার Saved Messages অথবা অন্য কোথাও Forward করে রাখুন।**"
            )

            # ৩০ মিনিট অপেক্ষা
            await asyncio.sleep(1800)

            # অটো ডিলিট
            await sent_file.delete()
            await notice.delete()
            await message.reply_text("🕒 **সময় শেষ!** নিরাপত্তার জন্য ফাইলটি মুছে ফেলা হয়েছে।")

        except Exception:
            await proc.edit("❌ **Error:** ফাইলটি পাওয়া যায়নি। আবার আপলোড করে নতুন লিঙ্ক নিন।")
    else:
        await message.reply_text("👋 **Welcome to AHRTSBD File Store**\n\nফাইল আপলোড করতে /upload লিখুন।")

# --- UPLOAD & MEDIA HANDLE ---
@app.on_message(filters.command("upload") & filters.private)
async def upload(client, message):
    user_data[message.from_user.id] = []
    await message.reply_text("📤 ফাইল পাঠান, সবগুলো পাঠানো শেষ হলে **✅ Finish** বাটনে ক্লিক করুন।", 
                             reply_markup=ReplyKeyboardMarkup([["✅ Finish"]], resize_keyboard=True))

@app.on_message(filters.private & ~filters.command(["start", "upload"]))
async def handle_media(client, message):
    user_id = message.from_user.id
    if message.text == "✅ Finish":
        if user_id in user_data and user_data[user_id]:
            file_id = user_data[user_id][0]
            link = f"https://t.me/{(await client.get_me()).username}?start={file_id}"
            await message.reply_text(f"✅ **আপনার লিঙ্ক তৈরি:**\n\n`{link}`", reply_markup=ReplyKeyboardRemove())
            user_data.pop(user_id)
    elif user_id in user_data:
        if message.document: user_data[user_id].append(message.document.file_id)
        elif message.video: user_data[user_id].append(message.video.file_id)
        elif message.photo: user_data[user_id].append(message.photo.file_id)
        await message.reply_text("📂 **সেভ হয়েছে!** আরও ফাইল থাকলে পাঠান অথবা শেষ করুন।")

app.run()
