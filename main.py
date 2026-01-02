from flask import Flask
import threading

# Render Port Fix
app_web = Flask(__name__)
@app_web.route('/')
def hello():
    return "AHRTSBD Bot is Running!"

def run_web():
    app_web.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web).start()

# এরপর আপনার বাকি কোড (Pyrogram এর অংশ) শুরু হবে...

import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# --- CONFIGURATION ---
API_ID = 20726200
API_HASH = "5e927fe061c2f988a843053b67f47da9"
BOT_TOKEN = "8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ"

app = Client("ahrtsbd_pro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary storage for upload process
user_data = {}

# --- START COMMAND (Link Handling & Auto Delete) ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.command) > 1:
        file_id = message.command[1]
        
        # 🟢 Animation Effect
        proc = await message.reply_text("⚡ **AHRTSBD Server-e connect hochhe...**")
        await asyncio.sleep(1)
        await proc.edit("📡 **File khunje paoya gechhe...**")
        await asyncio.sleep(1)
        await proc.edit("📤 **Apnar inbox-e pathano hochhe...**")
        
        try:
            # File pathano
            sent_file = await message.reply_document(
                document=file_id,
                caption="🚀 **Shared by: AHRTSBD Digital**\n\n⚠️ Eita 30 minute por delete hoye jabe."
            )
            await proc.delete()

            # Forward Notice
            notice = await message.reply_text(
                "✅ **File pathano hoyeche!**\n\n"
                "⚠️ **Sotorkobarta:**\n"
                "Copyright eronei eita **30 minute** por delete hoye jabe.\n\n"
                "📌 **Tai ekhon-e Saved Messages ba onno kothao Forward kore rakhen.**"
            )

            # 🕒 30 Minute Timer (1800 Seconds)
            await asyncio.sleep(1800)

            # Delete Logic
            await sent_file.delete()
            await notice.delete()
            await message.reply_text("🕒 **Somoy shesh!** Nirapottar khatire file-ti muche fela hoyeche.")

        except Exception:
            await proc.edit("❌ **Error:** File-ti paoya jayni ba server theke muche geche.")
    else:
        # Main Menu
        await message.reply_text(
            "👋 **Welcome to AHRTSBD File Store**\n\nFile upload korte /upload likhun.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Channel", url="https://t.me/+ec0RYUumPzVmYTc1")]
            ])
        )

# --- UPLOAD COMMAND ---
@app.on_message(filters.command("upload") & filters.private)
async def upload(client, message):
    user_data[message.from_user.id] = []
    await message.reply_text(
        "📤 **Upload Mode Active!**\n\nEkhon file pathan. Shob deoya shesh hole '✅ Finish' likhun ba button-e chap den.",
        reply_markup=ReplyKeyboardMarkup([["✅ Finish"]], resize_keyboard=True)
    )

# --- HANDLE MEDIA & FINISH ---
@app.on_message(filters.private & ~filters.command(["start", "upload"]))
async def handle_media(client, message):
    user_id = message.from_user.id
    
    if message.text == "✅ Finish":
        if user_id in user_data and user_data[user_id]:
            # Generate Link (Multiple file thakle prothomtar ID niye link hobe)
            file_id = user_data[user_id][0]
            link = f"https://t.me/{(await client.get_me()).username}?start={file_id}"
            
            await message.reply_text(
                f"✅ **Upload Complete!**\n\n🔗 **Link:** `{link}`",
                reply_markup=ReplyKeyboardRemove()
            )
            user_data.pop(user_id)
        else:
            await message.reply_text("❌ Kono file den ni!")
            
    elif user_id in user_data:
        # File type check kore save kora
        if message.document:
            user_data[user_id].append(message.document.file_id)
        elif message.video:
            user_data[user_id].append(message.video.file_id)
        elif message.photo:
            user_data[user_id].append(message.photo.file_id)
        
        await message.reply_text("📂 **Media saved!** Aro pathan ba ✅ Finish koren.")

app.run()
  
