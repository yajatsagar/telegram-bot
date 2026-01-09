import requests
import time
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# ================= CONFIG =================

BOT_TOKEN = "8431658256:AAFpuYSGZf8LklVtGJgxO1_n9buXzkDPXwc"
API_KEY = "nuvy"
API_URL = "https://aetherosint.site/cutieee/api.php"

ALLOWED_GROUP_ID = -1002178825948

PUBLIC_CHANNEL = "@Dark_Reaver"
PUBLIC_CHANNEL_LINK = "https://t.me/Dark_Reaver"

PRIVATE_CHANNEL_LINK = "https://t.me/+iMrddoNmV6k0M2Jl"
GROUP_INVITE_LINK = "https://t.me/+ocpvos9fMTgzZWQ1"

DAILY_LIMIT = 10

# ============== ENABLE LOGGING ==============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =========================================

user_usage = {}
verified_users = set()


def check_limit(user_id):
    now = time.time()
    if user_id not in user_usage:
        user_usage[user_id] = {"count": 0, "time": now}
        return True
    if now - user_usage[user_id]["time"] > 86400:
        user_usage[user_id] = {"count": 0, "time": now}
        return True
    return user_usage[user_id]["count"] < DAILY_LIMIT


async def is_user_in_public_channel(user_id, context):
    try:
        member = await context.bot.get_chat_member(PUBLIC_CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.error(f"Error checking public channel: {e}")
        return False


async def is_user_in_group(user_id, context):
    try:
        member = await context.bot.get_chat_member(ALLOWED_GROUP_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.error(f"Error checking group: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command from user: {update.effective_user.id}")
    await update.message.reply_text(
        "👋 *Welcome to DarkReaver Number to Info Lookup Bot*\n\n"
        "📱 To lookup number information, use:\n"
        "`/num <mobile_number>`\n\n"
        "Example: `/num 9876543210`",
        parse_mode="Markdown")

FAMPAY_API = "https://chumt-hvb29uo8d-okvaipro-svgs-projects.vercel.app/verify"

def check_fampay(number: str):
    try:
        r = requests.get(
            FAMPAY_API,
            params={"query": number},
            timeout=10
        )
        r.raise_for_status()
        return r.text.lower()
    except:
        return None


async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logger.info(f"Num command from user {user_id} in chat {chat_id}")
    
    # Send typing action to show bot is working
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Check if it's a private chat or group
    if update.effective_chat.type == "private":
        # 🔐 JOIN CHECK (CHANNEL + PRIVATE + GROUP)
        in_public = await is_user_in_public_channel(user_id, context)
        in_group = await is_user_in_group(user_id, context)

        if not in_public or not in_group:
            keyboard = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("📢 Join Public Channel",
                                         url=PUBLIC_CHANNEL_LINK)
                ],
                 [
                     InlineKeyboardButton("🔒 Join Private Channel",
                                          url=PRIVATE_CHANNEL_LINK)
                 ],
                 [
                     InlineKeyboardButton("👥 Join Official Group",
                                          url=GROUP_INVITE_LINK)
                 ]])

            await update.message.reply_text(
                "🚫 *Access Denied*\n\n"
                "To use this bot, you must join:\n"
                "• Public Channel\n"
                "• Private Channel\n"
                "• Official Group\n\n"
                "After joining, send `/num` again.",
                parse_mode="Markdown",
                reply_markup=keyboard)
            return

    if not check_limit(user_id):
        await update.message.reply_text("🚫 *Daily limit reached (10/day).*",
                                        parse_mode="Markdown")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /num <number>\n\nExample: `/num 9876543210`", parse_mode="Markdown")
        return

    number = context.args[0]
    
    # Validate number
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_text("❌ Please enter a valid mobile number (at least 10 digits)")
        return
    
    logger.info(f"Processing lookup for number: {number}")
    
    # Send processing message
    processing_msg = await update.message.reply_text("🔍 *Processing your request...*", parse_mode="Markdown")

    # Add timeout for the API request
    try:
        logger.info(f"Making API request to: {API_URL}")
        r = requests.get(API_URL,
                         params={
                             "key": API_KEY,
                             "type": "mobile",
                             "term": number
                         },
                         timeout=20)
        logger.info(f"API Response status: {r.status_code}")
    except requests.exceptions.Timeout:
        await processing_msg.edit_text("⚠️ API timeout. Please try again.")
        return
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        await processing_msg.edit_text("⚠️ Network error. Please try again.")
        return

    try:
        j = r.json()
        logger.info(f"API Response: {j}")
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        await processing_msg.edit_text("⚠️ API error. Please try again.")
        return

    if j.get("status") != "found":
        await processing_msg.edit_text("❌ No data found for this number.")
        return

    raw_data = j.get("data")
    data = raw_data[0] if isinstance(raw_data, list) else raw_data

    text = f"""
════════════════════════════════════
           ❄️  CREDIT  ❄️
            @Dark_Reaver
════════════════════════════════════

📱 Mobile Lookup Result
《《《  RESULT SUMMARY  》》》
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☛ *Address:* {data.get("address", "N/A")}
☛ *Alternate Mobile:* {data.get("alt", "N/A")}
☛ *Circle:* {data.get("circle", "N/A")}
☛ *Father Name:* {data.get("fname", "N/A")}
☛ *Id:* {data.get("_id", "N/A")}
☛ *ID:* {data.get("id", "N/A")}
☛ *Mobile:* {data.get("mobile", number)}
☛ *Name:* {data.get("name", "N/A")}
☛ *Name lower:* {data.get("name_lower", "N/A")}

════════════════════════════════════
           ❄️  CREDIT  ❄️
            @Dark_Reaver
════════════════════════════════════
"""

    filename = f"{number}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🔗 Official Channel 🔗",
                                 url=PUBLIC_CHANNEL_LINK)
        ],
         [
             InlineKeyboardButton(
                 "⭐ Add me to your Group ⭐",
                 url="https://t.me/darkreaverbot?startgroup=true")
         ]])

    # Delete processing message
    await processing_msg.delete()
    
    with open(filename, "rb") as file:
        await update.message.reply_document(
            document=file,
            filename=f"number_info_{number}.txt",
            caption="📱 *Mobile Lookup Result*",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    os.remove(filename)

    user_usage[user_id]["count"] += 1
    logger.info(f"Lookup completed for user {user_id}. Count: {user_usage[user_id]['count']}")


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    logger.info(f"Verify callback from user: {user_id}")
    
    verified_users.add(user_id)
    await query.answer("✅ Verified! Now send /num again.", show_alert=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Bot Help*\n\n"
        "Available commands:\n"
        "• /start - Start the bot\n"
        "• /num <number> - Lookup number information\n"
        "• /help - Show this help message\n\n"
        "Example: `/num 9876543210`",
        parse_mode="Markdown"
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Unknown command. Use /help to see available commands.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again.")


def main():
    logger.info("Starting bot...")
    
    # Try with increased timeouts
    try:
        app = ApplicationBuilder() \
            .token(BOT_TOKEN) \
            .read_timeout(30) \
            .write_timeout(30) \
            .connect_timeout(30) \
            .pool_timeout(30) \
            .build()
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        # Try alternative approach
        app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", num))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify_me"))
    
    # Unknown command handler (must be last)
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    logger.info("🤖 Bot is running and ready to accept commands...")
    print("\n" + "="*50)
    print("🤖 Bot Status: RUNNING")
    print(f"📱 Bot Username: @{(app.bot.username)}")
    print("📝 Commands available: /start, /num, /help")
    print("="*50 + "\n")
    
    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    main()