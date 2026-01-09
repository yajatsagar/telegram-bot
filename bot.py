import requests
import time
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ================= CONFIG =================

BOT_TOKEN = "8431658256:AAFpuYSGZf8LklVtGJgxO1_n9buXzkDPXwc"
API_KEY = "nuvy"
API_URL = "https://aetherosint.site/cutieee/api.php"

FAMPAY_API = "https://chumt-hvb29uo8d-okvaipro-svgs-projects.vercel.app/verify"

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
        "`/num <mobile_number>`\n\n"
        "💳 To lookup UPI ID information, use:\n"
        "`/fam <upi_id>`\n\n",
        parse_mode="Markdown")


async def fam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check joins
    in_public = await is_user_in_public_channel(user_id, context)
    in_group = await is_user_in_group(user_id, context)
    
    if not in_public or not in_group:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Public Channel", url=PUBLIC_CHANNEL_LINK)],
            [InlineKeyboardButton("🔒 Join Private Channel", url=PRIVATE_CHANNEL_LINK)],
            [InlineKeyboardButton("👥 Join Official Group", url=GROUP_INVITE_LINK)]
        ])
        await update.message.reply_text(
            "🚫 *Access Denied*\n\nTo use this bot, you must join:\n"
            "• Public Channel\n• Private Channel\n• Official Group\n\n"
            "After joining, send `/fam` again.",
            parse_mode="Markdown",
            reply_markup=keyboard)
        return
    
    if not check_limit(user_id):
        await update.message.reply_text("🚫 *Daily limit reached (10/day).*", parse_mode="Markdown")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ Usage: /fam <upi_id>\n\n"
            "*This API converts UPI ID to phone number*\n\n"
            "*Examples:*\n"
            "`/fam 9971591849@fam`\n"
            "`/fam 1234567890@okhdfcbank`\n"
            "`/fam someone@upi`",
            parse_mode="Markdown")
        return
    
    upi_id = context.args[0]
    processing_msg = await update.message.reply_text(f"🔍 *Querying: *`{upi_id}`\n\nFetching phone number from API...", parse_mode="Markdown")
    
    try:
        # Call the API
        api_url = f"{FAMPAY_API}?query={upi_id}"
        response = requests.get(api_url, timeout=15)
        
        # Create result message
        result_message = f"💳 *UPI to Phone Lookup*\n\n"
        result_message += f"*UPI ID:* `{upi_id}`\n"
        result_message += f"*API URL:* `{api_url}`\n\n"
        
        if response.status_code == 200:
            try:
                data = response.json()
                result_message += f"*Status:* ✅ Success\n"
                result_message += f"*Code:* `{data.get('code', 'N/A')}`\n"
                result_message += f"*Message:* `{data.get('message', '')}`\n\n"
                
                if data.get("code") == "SUCCESS" and "data" in data:
                    verify_data = data["data"].get("verify_chumts", [{}])[0] if data["data"].get("verify_chumts") else {}
                    
                    phone_number = verify_data.get("upi_number")
                    result_message += f"📱 *Phone Number:* `{phone_number if phone_number else 'Not found in API response'}`\n"
                    
                    if verify_data.get("name"):
                        result_message += f"👤 *Name:* {verify_data.get('name')}\n"
                    if verify_data.get("acc_no"):
                        result_message += f"🏦 *Account:* `{verify_data.get('acc_no')}`\n"
                    if verify_data.get("ifsc"):
                        result_message += f"🔢 *IFSC:* `{verify_data.get('ifsc')}`\n"
                    
                else:
                    result_message += f"⚠️ *Data:* No verify_chumts found in response\n"
                
                # Add raw JSON for debugging
                result_message += f"\n📄 *Raw JSON Response:*\n```json\n{json.dumps(data, indent=2)}\n```"
                
            except json.JSONDecodeError:
                result_message += f"📄 *Raw Text Response:*\n```\n{response.text}\n```"
        else:
            result_message += f"❌ *Status:* Error {response.status_code}\n"
            result_message += f"📄 *Response:*\n```\n{response.text}\n```"
        
        await processing_msg.edit_text(result_message, parse_mode="Markdown")
        
        # Update usage if successful
        if response.status_code == 200:
            user_usage[user_id]["count"] += 1
            
    except Exception as e:
        await processing_msg.edit_text(f"❌ *Error:* {str(e)}", parse_mode="Markdown")


async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id

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
        await update.message.reply_text("❌ Usage: /num <number>")
        return

    number = context.args[0]

    r = requests.get(API_URL,
                     params={
                         "key": API_KEY,
                         "type": "mobile",
                         "term": number
                     })
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

    os.remove(filename)

    user_usage[user_id]["count"] += 1


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    verified_users.add(user_id)

    await query.answer("✅ Verified! Now send /num again.", show_alert=True)


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("num", num))
app.add_handler(CommandHandler("fam", fam))
app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify_me"))

print("🤖 Bot is running...")
app.run_polling()