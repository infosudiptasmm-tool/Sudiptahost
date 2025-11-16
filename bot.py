import os
import json
import time
from telebot import TeleBot, types

# ---------------------------
# CONFIGURATION
# ---------------------------
BOT_TOKEN = "8276744757:AAHJj9EmHWVl4kwPhoSl3YP9QQsU_W2JRLY"  # Replace with your bot token
OWNER_USERNAME = "@JOINXT00L"
UPDATES_CHANNEL = "https://t.me/joinxhost"
FREE_LIMIT = 2  # Free users can upload 2 files

bot = TeleBot(BOT_TOKEN)

# ---------------------------
# DATABASE
# ---------------------------
DB_FILE = "database.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}, "files": {}}, f, indent=4)


def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


# ---------------------------
# MAIN MENU BUTTONS
# ---------------------------
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Updates Channel", url=UPDATES_CHANNEL))
    markup.add(types.InlineKeyboardButton("🗂 Upload File", callback_data="upload"))
    markup.add(types.InlineKeyboardButton("📁 Check Files", callback_data="files"))
    markup.add(types.InlineKeyboardButton("⚡ Bot Speed", callback_data="speed"))
    markup.add(types.InlineKeyboardButton("📊 Statistics", callback_data="stats"))
    markup.add(types.InlineKeyboardButton("☎️ Contact Owner", url=f"https://t.me/{OWNER_USERNAME.replace('@','')}"))
    return markup


# ---------------------------
# START COMMAND
# ---------------------------
@bot.message_handler(commands=['start'])
def start(message):
    db = load_db()
    user_id = str(message.chat.id)

    if user_id not in db["users"]:
        db["users"][user_id] = {"files": 0}
        save_db(db)

    username = message.from_user.username or "No Username"

    text = f"""
<b>✨ Welcome to SudiptaHost</b>

<b>Your Details:</b>
• <b>User ID:</b> <code>{message.chat.id}</code>
• <b>Username:</b> @{username}
• <b>Status:</b> Free User
• <b>File Upload Limit:</b> {db['users'][user_id]['files']} / {FREE_LIMIT}
• <b>Running Bots:</b> 0

<b>Choose an option below:</b>
"""

    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode="html")


# ---------------------------
# CALLBACK HANDLERS
# ---------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    # UPLOAD FILE
    if call.data == "upload":
        bot.send_message(call.message.chat.id, "📤 <b>Send your .py or .js file now.</b>", parse_mode="html")
        bot.register_next_step_handler(call.message, save_uploaded_file)

    # CHECK FILES
    elif call.data == "files":
        db = load_db()
        user_id = str(call.message.chat.id)

        files = db["files"].get(user_id, [])

        if not files:
            bot.send_message(call.message.chat.id, "❌ No files found.")
            return

        msg = "<b>Your Uploaded Files:</b>\n\n"
        for i, f in enumerate(files, start=1):
            msg += f"{i}. {f}\n"

        bot.send_message(call.message.chat.id, msg, parse_mode="html")

    # BOT SPEED
    elif call.data == "speed":
        start = time.time()
        msg = bot.send_message(call.message.chat.id, "Checking speed...")
        end = time.time()
        ping = int((end - start) * 1000)
        bot.edit_message_text(f"⚡ <b>Bot Speed:</b> {ping} ms", call.message.chat.id, msg.message_id, parse_mode="html")

    # STATISTICS
    elif call.data == "stats":
        db = load_db()
        users = len(db["users"])
        files_count = sum(len(v) for v in db["files"].values())

        msg = f"""
<b>📊 SudiptaHost Statistics</b>

<b>Total Users:</b> {users}
<b>Total Uploaded Files:</b> {files_count}
"""

        bot.send_message(call.message.chat.id, msg, parse_mode="html")


# ---------------------------
# SAVE UPLOADED FILE
# ---------------------------
def save_uploaded_file(message):
    db = load_db()
    user_id = str(message.chat.id)

    if db["users"][user_id]["files"] >= FREE_LIMIT:
        bot.send_message(message.chat.id, "❌ You reached your free limit (2 files).")
        return

    if not message.document:
        bot.send_message(message.chat.id, "❌ Please send a valid file.")
        return

    file_info = bot.get_file(message.document.file_id)
    file_data = bot.download_file(file_info.file_path)

    filename = message.document.file_name

    if not os.path.exists("user_files"):
        os.makedirs("user_files")

    with open(f"user_files/{filename}", "wb") as f:
        f.write(file_data)

    db["files"].setdefault(user_id, []).append(filename)
    db["users"][user_id]["files"] += 1
    save_db(db)

    bot.send_message(message.chat.id, f"✅ <b>File Uploaded Successfully:</b>\n<code>{filename}</code>", parse_mode="html")


# ---------------------------
# START BOT
# ---------------------------
bot.infinity_polling()
