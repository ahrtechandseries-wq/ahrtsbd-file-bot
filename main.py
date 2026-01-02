import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION ---
API_ID = 20726200
API_HASH = "5e927fe061c2f988a843053b67f47da9"
BOT_TOKEN = "8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ"

app = Client("ahrtsbd_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER (Render Fix) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "AHRTSBD is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# ডাটা জমা রাখার জন্য (সাময়িকভাবে)
user_states = {}

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.command) > 1:
        file_id = message.command[1]
        wait_msg = await message.reply_text("⏳ **ফাইলটি আনা হচ্ছে...**")
        
        try:
            # ফাইল পাঠানো (আপনার দেওয়া ফাইল টাইপ লজিক অনুযায়ী)
            sent_file = await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=file_id,
                caption="🚀 **Shared by: AHRTSBD**\n\n⚠️ এটি ৩০ মিনিট পর ডিলিট হবে।"
            )
            await wait_msg.delete()

            notice = await message.reply_text(
                "✅ **ফাইল সফলভাবে পাঠানো হয়েছে!**\n\n"
                "📌 এটি ৩০ মিনিট পর ডিলিট হবে। এখনই এটি **Saved Messages**-এ ফরওয়ার্ড করে রাখুন।"
            )

            # --- ৩০ মিনিট পর ডিলিট লজিক ---
            await asyncio.sleep(1800) # ১৮০০ সেকেন্ড = ৩০ মিনিট
            await sent_file.delete()
            await notice.delete()
            await message.reply_text("🕒 **সময় শেষ!** ফাইলটি মুছে ফেলা হয়েছে।")

        except Exception:
            await wait_msg.edit("❌ ফাইলটি পাওয়া যায়নি।")
    else:
        await message.reply_text(
            "<b>AHRTSBD</b>\n\n"
            "Upload multiple files securely and get a private share link.\n\n"
            "⚡ <b>Steps:</b>\n"
            "• Type /upload\n"
            "• Send your files\n"
            "• Type ✅ to finish",
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📤 Upload File", callback_data="upload_req")
            ]])
        )

# --- UPLOAD LOGIC ---
@app.on_message(filters.command("upload") | filters.regex("📤 Upload File"))
async def upload_cmd(client, message):
    user_states[message.from_user.id] = True
    keyboard = ReplyKeyboardMarkup([["✅"]], resize_keyboard=True)
    await message.reply_text("👉 আমাকে ফাইল পাঠান। শেষ হলে ✅ বাটনে ক্লিক করুন।", reply_markup=keyboard)

@app.on_message(filters.private & ~filters.command(["start", "upload"]))
async def handle_media(client, message):
    user_id = message.from_user.id
    
    if message.text == "✅":
        user_states.pop(user_id, None)
        await message.reply_text("✅ আপলোড প্রসেস শেষ।", reply_markup=ReplyKeyboardRemove())
        return

    if user_id in user_states:
        media = message.photo or message.video or message.audio or message.document or message.animation or message.sticker
        
        if media:
            # ফাইলের ID নেওয়া
            if message.photo: file_id = message.photo.file_id
            elif message.video: file_id = message.video.file_id
            else: file_id = media.file_id
            
            me = await client.get_me()
            shareable_link = f"https://t.me/{me.username}?start={file_id}"
            
            await message.reply_text(
                f"✅ **মিডিয়া সেভ হয়েছে!**\n\n🔗 আপনার লিঙ্ক:\n`{shareable_link}`\n\nআরও পাঠাতে পারেন অথবা ✅ ক্লিক করুন।"
            )
        else:
            await message.reply_text("❌ অসংগতিপূর্ণ ফাইল।")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    app.run()
    
