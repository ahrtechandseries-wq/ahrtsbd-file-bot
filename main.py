import asyncio
import os
import threading
from flask import Flask
from telethon import TelegramClient, events, Button

# --- CONFIGURATION (Fixed) ---
API_ID = 20726200
API_HASH = "5e927fe061c2f988a843053b67f47da9"
BOT_TOKEN = "8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ"

bot = TelegramClient('ahrtsbd_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- WEB SERVER FOR RENDER ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "AHRTSBD IS LIVE"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- START & LINK HANDLING ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if len(event.text) > 7:
        file_id = event.text.split(' ')[1]
        wait = await event.reply("⏳ **অপেক্ষা করুন... ফাইলটি আনা হচ্ছে...**")
        try:
            # ফাইল পাঠানো (Telethon সরাসরি ফাইল আইডি সাপোর্ট করে)
            sent_file = await bot.send_file(event.chat_id, file_id, caption="🚀 **Shared by: AHRTSBD**\n\n⚠️ নিরাপত্তার জন্য এটি ৩০ মিনিট পর ডিলিট হবে।")
            await wait.delete()
            notice = await event.reply("✅ **ফাইল পাঠানো হয়েছে!** এখনই এটি আপনার Saved Messages-এ ফরওয়ার্ড করে রাখুন।")
            
            # ৩০ মিনিট ডিলিট টাইমার
            await asyncio.sleep(1800)
            await bot.delete_messages(event.chat_id, [sent_file.id, notice.id])
        except Exception as e:
            await wait.edit(f"❌ ফাইলটি পাওয়া যায়নি। আবার আপলোড করে নতুন লিঙ্ক নিন।")
    else:
        await event.reply(
            "👋 **স্বাগতম AHRTSBD ফাইল স্টোর বোটে!**\n\n"
            "📤 ফাইল আপলোড করে লিঙ্ক তৈরি করতে চাইলে নিচে ক্লিক করুন বা লিখুন: /upload",
            buttons=[Button.text("/upload", resize=True)]
        )

# --- UPLOAD HANDLING ---
user_uploading = {}

@bot.on(events.NewMessage(pattern='/upload'))
async def upload(event):
    user_uploading[event.sender_id] = True
    await event.reply("📤 **এখন আপনার ফাইলটি পাঠান।**\n\nসবগুলো পাঠানো শেষ হলে নিচের **✅ Finish** বাটনে ক্লিক করুন।", 
                     buttons=[Button.text("✅ Finish", resize=True)])

@bot.on(events.NewMessage)
async def handle_all(event):
    if event.text == "✅ Finish":
        user_uploading.pop(event.sender_id, None)
        await event.reply("✅ **আপলোড প্রসেস শেষ হয়েছে।**", buttons=Button.clear())
        return

    if event.sender_id in user_uploading and event.media:
        # ফাইলের পারমানেন্ট আইডি নেওয়া
        file_id = event.file.id
        me = await bot.get_me()
        link = f"https://t.me/{me.username}?start={file_id}"
        await event.reply(f"✅ **আপনার শেয়ারিং লিঙ্ক:**\n\n`{link}`\n\nএই লিঙ্কটি কপি করে শেয়ার করুন।")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.run_until_disconnected()
    
