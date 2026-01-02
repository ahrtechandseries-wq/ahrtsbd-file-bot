    @classmethod
    async def process_files(
        cls,
        client: Client,
        message: Message,
        file_data: list[FileResolverModel],
    ) -> Message:
        "Handles file backups"

        unique_link = f"{uuid.uuid4().int}"
        file_link = DataEncoder.encode_data(unique_link)
        file_origin = config.BACKUP_CHANNEL if options.settings.BACKUP_FILES else message.chat.id
        file_datas = [i.model_dump() for i in file_data]

        add_file = await cls.database.add_file(file_link=file_link, file_origin=file_origin, file_data=file_datas)

        if add_file:
            link = f"https://t.me/{client.me.username}?start={file_link}"
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Share URL", url=f"https://t.me/share/url?url={link}")]],
            )

            # লিঙ্ক পাঠানোর মেসেজটি সেভ করে রাখা
            sent_msg = await message.reply(
                text=f"✅ **লিঙ্ক তৈরি হয়েছে!**\n\n🔗 **লিঙ্ক:** `{link}`\n\n⚠️ নিরাপত্তার জন্য এই মেসেজটি ৩০ মিনিট পর ডিলিট হয়ে যাবে।",
                quote=True,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )

            # --- অটো-ডিলিট লজিক শুরু ---
            async def auto_delete():
                await asyncio.sleep(1800)  # ১৮০০ সেকেন্ড = ৩০ মিনিট
                try:
                    await sent_msg.delete()  # বোটের পাঠানো লিঙ্ক মেসেজটি ডিলিট হবে
                    await message.delete()   # ইউজারের পাঠানো অরিজিনাল ফাইলটি ডিলিট হবে
                except:
                    pass # মেসেজ আগে ডিলিট হয়ে গেলে এরর এড়াতে

            asyncio.create_task(auto_delete())
            return sent_msg
            # --- অটো-ডিলিট লজিক শেষ ---

        return await message.reply("Couldn't add files to database")
        
