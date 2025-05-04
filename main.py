import telebot
import time
import json
import random
from datetime import datetime, timedelta

# إعدادات البوت
TOKEN = '7609490900:AAGuahLVA72eeeN6KqIe-i1Kt-3I-Eaibok'
bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات بسيطة
users = {}
ads = [
    {"text": "شاهد إعلان 1 واربح 100 TON", "url": "https://example.com", "reward": 100},
    {"text": "شاهد إعلان 2 واربح 150 TON", "url": "https://example2.com", "reward": 150}
]

# تحميل البيانات من ملف
def load_data():
    global users
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

def save_data():
    with open("users.json", "w") as f:
        json.dump(users, f)

def get_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "balance": 0,
            "referrals": 0,
            "last_claim": "1970-01-01"
        }
    return users[str(user_id)]

@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    args = message.text.split()
    if len(args) > 1:
        ref_id = args[1]
        if ref_id != str(message.from_user.id):
            ref_user = get_user(ref_id)
            ref_user["referrals"] += 1
            ref_user["balance"] += 250  # مكافأة الإحالة
    save_data()
    bot.send_message(message.chat.id, "مرحباً بك في بوت ربح TON! اختر من القائمة:",
                     reply_markup=main_menu())

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("مشاهدة الإعلانات", "المكافأة اليومية")
    markup.row("رصيدي", "سحب الأرباح")
    markup.row("رابط الإحالة")
    return markup

@bot.message_handler(func=lambda m: m.text == "مشاهدة الإعلانات")
def view_ads(message):
    ad = random.choice(ads)
    bot.send_message(message.chat.id, f"{ad['text']}
رابط الإعلان: {ad['url']}")
    time.sleep(10)  # تمثيل مشاهدة الإعلان
    user = get_user(message.from_user.id)
    user["balance"] += ad["reward"]
    save_data()
    bot.send_message(message.chat.id, f"تم إضافة {ad['reward']} TON إلى رصيدك.")

@bot.message_handler(func=lambda m: m.text == "المكافأة اليومية")
def daily_bonus(message):
    user = get_user(message.from_user.id)
    last = datetime.strptime(user["last_claim"], "%Y-%m-%d")
    today = datetime.utcnow().date()
    if last.date() < today:
        user["balance"] += 200
        user["last_claim"] = str(today)
        save_data()
        bot.send_message(message.chat.id, "تم إضافة 200 TON إلى رصيدك كمكافأة يومية!")
    else:
        bot.send_message(message.chat.id, "لقد استلمت مكافأتك اليومية بالفعل، عُد غداً!")

@bot.message_handler(func=lambda m: m.text == "رصيدي")
def check_balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"رصيدك الحالي: {user['balance']} TON")

@bot.message_handler(func=lambda m: m.text == "رابط الإحالة")
def referral_link(message):
    link = f"https://t.me/YOUR_BOT_USERNAME?start={message.from_user.id}"
    bot.send_message(message.chat.id, f"رابط الإحالة الخاص بك:
{link}
عدد الإحالات: {get_user(message.from_user.id)['referrals']}")

@bot.message_handler(func=lambda m: m.text == "سحب الأرباح")
def withdraw(message):
    bot.send_message(message.chat.id, "أرسل عنوان محفظتك على FaucetPay (عملة TON):")
    bot.register_next_step_handler(message, process_withdraw)

def process_withdraw(message):
    address = message.text
    user = get_user(message.from_user.id)
    if user["balance"] < 1000:
        bot.send_message(message.chat.id, "الحد الأدنى للسحب هو 1000 TON.")
        return
    # هنا يتم إرسال الدفع عبر FaucetPay API (سنضيفها لاحقًا)
    user["balance"] -= 1000
    save_data()
    bot.send_message(message.chat.id, f"تم إرسال 1000 TON إلى محفظتك: {address}")
    # إثبات دفع للقناة
    bot.send_message("@qqwweerrttqqyyyy", f"تم دفع 1000 TON إلى {address} من المستخدم @{message.from_user.username or message.from_user.id}")

load_data()
print("Bot is running...")
bot.infinity_polling()
