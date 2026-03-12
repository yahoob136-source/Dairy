#!/usr/bin/env python3
import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

BOT_TOKEN = "8787082521:AAFQGwgvK0zCWDm7UW5cHhsJgUxeG0d6Qwg"
PINTEREST_LINK = "https://pin.it/5GtgARcTs"
INFO_CHANNEL_LINK = "https://t.me/yourchannel"
ADMIN_ID = 7575318765
VIDEO_DELETE_SECONDS = 300

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stored_video = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📌 Pinterest Subscribe", url=PINTEREST_LINK)],
        [InlineKeyboardButton("📢 Info Channel Join", url=INFO_CHANNEL_LINK)],
        [InlineKeyboardButton("🎬 Video Dekhein", callback_data="watch_video")],
    ]
    await update.message.reply_text(
        "👋 *Welcome!*\n\n"
        "⬇️ Neeche diye buttons pe click karein:\n\n"
        "📌 *Pinterest* – Hamare page ko subscribe karein\n"
        "📢 *Info Channel* – Important updates ke liye join karein\n"
        "🎬 *Video* – Special video dekhein _(5 min baad delete ho jaegi!)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def watch_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not stored_video.get("file_id"):
        await query.message.reply_text("⚠️ Abhi koi video available nahi hai.\nThodi der baad try karein! 🙏")
        return
    sent = await query.message.reply_video(
        video=stored_video["file_id"],
        caption=(
            f"{stored_video.get('caption', '🎬 Special Video')}\n\n"
            "⏳ *Yeh video 5 minute baad delete ho jaegi!*\n"
            "📌 Pinterest subscribe karna mat bhoolein!"
        ),
        parse_mode="Markdown"
    )
    context.application.create_task(
        delete_after_timer(context, sent.chat_id, sent.message_id)
    )


async def delete_after_timer(context, chat_id, message_id):
    await asyncio.sleep(VIDEO_DELETE_SECONDS)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        notice = await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "🗑️ *Video delete ho gayi!*\n\n"
                "📌 [Pinterest Subscribe karein](" + PINTEREST_LINK + ")\n"
                "📢 [Info Channel Join karein](" + INFO_CHANNEL_LINK + ")\n\n"
                "_(Yeh message bhi 1 min mein delete hoga)_"
            ),
            parse_mode="Markdown"
        )
        await asyncio.sleep(60)
        await context.bot.delete_message(chat_id=chat_id, message_id=notice.message_id)
    except Exception as e:
        logger.warning(f"Delete error: {e}")


async def receive_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    video = update.message.video or update.message.document
    if video:
        stored_video["file_id"] = video.file_id
        stored_video["caption"] = update.message.caption or "🎬 Special Video"
        await update.message.reply_text(
            "✅ *Video save ho gayi!*\n\nAb users dekh sakte hain.\n5 min baad auto-delete hogi! ⏳",
            parse_mode="Markdown"
        )


async def set_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("📤 *Ab video bhejo is bot ko!*", parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if stored_video.get("file_id"):
        await update.message.reply_text(f"✅ Video available hai!\nCaption: {stored_video.get('caption', 'N/A')}")
    else:
        await update.message.reply_text("❌ Koi video set nahi hai abhi.")


async def update_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    global INFO_CHANNEL_LINK
    if context.args:
        INFO_CHANNEL_LINK = context.args[0]
        await update.message.reply_text(f"✅ Channel link update ho gaya!\n{INFO_CHANNEL_LINK}")
    else:
        await update.message.reply_text("❌ Link bhejo!\nExample: /setchannel https://t.me/apnachannel")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setvideo", set_video_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("setchannel", update_channel))
    app.add_handler(CallbackQueryHandler(watch_video, pattern="^watch_video$"))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, receive_video))
    print("🤖 Bot chal raha hai 24/7...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
