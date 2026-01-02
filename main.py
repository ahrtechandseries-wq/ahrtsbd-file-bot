import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

# --- CONFIGURATION ---
# Render এর Environment Variables থেকে তথ্য নিবে, না থাকলে ডিফল্টটি ব্যবহার করবে
API_ID = int(os.environ.get("API_ID", 20726200))
API_HASH = os.environ.get("API_HASH", "5e927fe061c2f988a843053b67f47da9")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "EIKHANE_APNAR_TOKEN_DIN")

app = Client("ahrtsbd_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- FLASK WEB SERVER (For Render Keep-Alive) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "AHRTSBD Bot is Running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- GLOBAL DATA ---
user_data = {}

# --- COMMANDS ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    # যদি লিঙ্কের মাধ্যমে ফাইল এক্সেস করে
    if len(message.command) > 1:
        file_id = message.command[1]
        wait_msg = await message.reply_text("⏳ **অপেক্ষা করুন, ফাইলটি সার্ভার থেকে আনা হচ্ছে...**")
        
        try:
            # ফাইল পাঠানো
            sent_file = await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=file_id,
                caption="🚀 **Shared by: AHRTSBD**\n\n⚠️ নিরাপত্তার জন্য এই ফাইলটি ৩০ মিনিট পর ডিলিট হবে।"
            )
            await wait_msg.delete()

            notice = await message.reply_text(
                "✅ **ফাইল সফলভাবে পাঠানো হয়েছে!**\n\n"
                "📌 **সতর্কতা:** কপিরাইট এড়াতে ৩০ মিনিট পর ফাইলটি মুছে যাবে। তাই এখনই এটি আপনার **Saved Messages**-এ ফরওয়ার্ড করে রাখুন।"
            )

            # ৩০ মিনিট অপেক্ষা করে ডিলিট করা
            await asyncio.sleep(1800)
            try:
                await sent_file.delete()
                await notice.delete()
                await message.reply_text("🕒 **সময় শেষ!** ফাইলটি অটোমেটিক ডিলিট করা হয়েছে।")
            except:
                pass # যদি ইউজার আগেই ডিলিট করে দেয়

        except Exception as e:
            await wait_msg.edit(f"❌ **Error:** ফাইলটি পাওয়া যায়নি। আবার আপলোড করে নতুন লিঙ্ক নিন।")
    else:
        # সাধারণ স্টার্ট মেসেজ
        await message.reply_text(
            "👋 **স্বাগতম AHRTSBD ফাইল স্টোর বোটে!**\n\n"
            "📤 ফাইল আপলোড করে লিঙ্ক তৈরি করতে চাইলে নিচে ক্লিক করুন বা লিখুন: /upload",
            reply_markup=ReplyKeyboardMarkup([["/upload"]], resize_keyboard=True)
        )

@app.on_message(filters.command("upload") & filters.private)
async def upload_init(client, message):
    user_data[message.from_user.id] = []
    await message.reply_text(
        "📤 **এখন আপনার ফাইলটি (ভিডিও/ডকুমেন্ট/ফটো) পাঠান।**\n\n"
        "সবগুলো পাঠানো শেষ হলে নিচের **✅ Finish** বাটনে ক্লিক করুন।",
        reply_markup=ReplyKeyboardMarkup([["✅ Finish"]], resize_keyboard=True)
    )

@app.on_message(filters.private & ~filters.command(["start", "upload"]))
async def handle_media(client, message):
    user_id = message.from_user.id
    
    if message.text == "✅ Finish":
        if user_id in user_data and user_data[user_id]:
            first_file_id = user_data[user_id][0]
            bot_info = await client.get_me()
            link = f"https://t.me/{bot_info.username}?start={first_file_id}"
            
            await message.reply_text(
                f"✅ **আপনার ফাইলটি সেভ করা হয়েছে!**\n\n"
                f"🔗 **শেয়ারিং লিঙ্ক:**\n`{link}`\n\n"
                "এই লিঙ্কটি কপি করে শেয়ার করতে পারেন।",
                reply_markup=ReplyKeyboardRemove()
            )
            user_data.pop(user_id)
        else:
            await message.reply_text("❌ আপনি কোনো ফাইল পাঠাননি! আগে ফাইল পাঠান।")
            
    elif user_id in user_data:
        # ফাইল আইডি সংগ্রহ করা
        file_id = None
        if message.document: file_id = message.document.file_id
        elif message.video: file_id = message.video.file_id
        elif message.photo: file_id = message.photo.file_id
        
        if file_id:
            user_data[user_id].append(file_id)
            await message.reply_text("📂 **ফাইলটি সেভ হয়েছে!** আরও থাকলে পাঠান অথবা ফিনিশ করুন।")

# --- START BOT AND WEB SERVER ---
if __name__ == "__main__":
    # ওয়েব সার্ভার ব্যাকগ্রাউন্ডে চালানো
    threading.Thread(target=run_web, daemon=True).start()
    # বোট রান করা
    app.run()
                
