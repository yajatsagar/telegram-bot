import requests
import time
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\nUse this command:\n/num <mobile_number>",
        parse_mode="Markdown"
    )

async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id

    # 1️⃣ Group check
    if chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text(
            "🚫 Use this bot in the official group only."
        )
        return

    # 2️⃣ Verification check (ONLY THIS)
    if user_id not in verified_users:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Public Channel", url=PUBLIC_CHANNEL_LINK)],
            [InlineKeyboardButton("🔒 Join Private Channel", url=PRIVATE_CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I Joined", callback_data="verify_me")]
        ])

        await update.message.reply_text(
            "🚫 Access Denied!\n\nJoin channels and press **I Joined**.",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return   # 🔴 THIS RETURN IS CRITICAL


    if not check_limit(user_id):
        await update.message.reply_text("🚫 *Daily limit reached (10/day).*", parse_mode="Markdown")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /num <number>")
        return

    number = context.args[0]

    r = requests.get(API_URL, params={"key": API_KEY, "type": "mobile", "term": number})
    try:
        j = r.json()
    except:
        await update.message.reply_text("⚠️ API error.")
        return

    if j.get("status") != "found":
        await update.message.reply_text("❌ No data found.")
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

    await update.message.reply_document(open(filename, "rb"))
    os.remove(filename)

    user_usage[user_id]["count"] += 1

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    verified_users.add(user_id)

    await query.answer(
        "✅ Verified! Now send /num again.",
        show_alert=True
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("num", num))
app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify_me"))

print("🤖 Bot is running...")
app.run_polling()
