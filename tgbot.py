import logging
import requests
import time
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

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
    except:
        return False


async def is_user_in_group(user_id, context):
    try:
        member = await context.bot.get_chat_member(ALLOWED_GROUP_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to DarkReaver Number to Info Lookup Bot*\n\n"
        "📱 To lookup number information, use:\n"
        "`/num <mobile_number>`\n\n",
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
    chat = update.effective_chat
    user_id = update.effective_user.id
    
    logging.info(f"[/num] User {user_id} called /num with args: {context.args}")

    # 🔐 JOIN CHECK (CHANNEL + PRIVATE + GROUP)
    try:
        in_public = await is_user_in_public_channel(user_id, context)
        logging.info(f"[/num] User {user_id} in public channel: {in_public}")
    except Exception as e:
        logging.exception(f"[/num] Error checking public channel for user {user_id}")
        in_public = False
    
    try:
        in_group = await is_user_in_group(user_id, context)
        logging.info(f"[/num] User {user_id} in group: {in_group}")
    except Exception as e:
        logging.exception(f"[/num] Error checking group membership for user {user_id}")
        in_group = False

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

        logging.info(f"[/num] Access denied for user {user_id} (in_public={in_public}, in_group={in_group})")
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
        logging.info(f"[/num] Daily limit reached for user {user_id}")
        await update.message.reply_text("🚫 *Daily limit reached (10/day).*",
                                        parse_mode="Markdown")
        return

    if len(context.args) != 1:
        logging.info(f"[/num] Invalid args for user {user_id}: {context.args}")
        await update.message.reply_text("❌ Usage: /num <number>")
        return

    number = context.args[0]
    logging.info(f"[/num] Looking up number: {number}")

    try:
        r = requests.get(API_URL,
                         params={
                             "key": API_KEY,
                             "type": "mobile",
                             "term": number
                         },
                         timeout=10)
        logging.info(f"[/num] API response status: {r.status_code}")
        j = r.json()
        logging.info(f"[/num] API response type: {type(j).__name__}, content: {j}")
    except Exception as e:
        logging.exception(f"[/num] API request failed for number {number}")
        await update.message.reply_text("⚠️ API error.")
        return

    # Handle both list and dict responses
    if isinstance(j, list):
        if not j or len(j) == 0:
            logging.info(f"[/num] Empty list response for number {number}")
            await update.message.reply_text("❌ No data found.")
            return
        data = j[0]
        logging.info(f"[/num] Using first element from list: {data}")
    elif isinstance(j, dict):
        if j.get("status") != "found":
            logging.info(f"[/num] No data found for number {number}, status: {j.get('status')}")
            await update.message.reply_text("❌ No data found.")
            return
        raw_data = j.get("data")
        data = raw_data[0] if isinstance(raw_data, list) else raw_data
        logging.info(f"[/num] Parsed data from dict: {data}")
    else:
        logging.error(f"[/num] Unexpected API response type: {type(j).__name__}")
        await update.message.reply_text("⚠️ Unexpected API response format.")
        return

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

    try:
        filename = f"{number}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        logging.info(f"[/num] Created file: {filename}")

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

        with open(filename, "rb") as file:
            await update.message.reply_document(document=file,
                                                caption="📱 *Mobile Lookup Result*",
                                                parse_mode="Markdown",
                                                reply_markup=keyboard)
        logging.info(f"[/num] Sent document to user {user_id}")

        os.remove(filename)
        user_usage[user_id]["count"] += 1
        logging.info(f"[/num] Completed lookup for user {user_id}, usage count: {user_usage[user_id]['count']}")
    except Exception as e:
        logging.exception(f"[/num] Error sending document to user {user_id}")
        await update.message.reply_text(f"❌ Error sending result: {str(e)}")



async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    verified_users.add(user_id)

    await query.answer("✅ Verified! Now send /num again.", show_alert=True)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Pong!")
    except Exception:
        logging.exception("Failed to reply to /ping")


async def log_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log incoming updates for debugging; don't auto-reply to avoid spam
    logging.info("Incoming update from %s: %s", update.effective_user.id if update.effective_user else None, update)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.exception("Exception while handling update: %s", update)


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("num", num))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_messages))
app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify_me"))
app.add_error_handler(error_handler)

print("🤖 Bot is running...")
try:
    # Use drop_pending_updates to clear webhooks/pending updates and start polling
    app.run_polling(drop_pending_updates=True)
except Exception:
    logging.exception("Bot terminated with an exception")
