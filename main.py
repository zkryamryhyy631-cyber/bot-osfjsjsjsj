import os
import re
import json
import random
from datetime import datetime
import pytz
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Config & Variables
ADMIN = 7145036494
TOKEN = os.environ.get("BOT_TOKEN")
CHECK_TOKEN = 

# Ensure Database directories
if not os.path.exists("database"):
    os.makedirs("database")

# Helper Functions
def bot(method, datas=None):
    if datas is None:
        datas = {}
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        res = requests.post(url, data=datas)
        return res.json()
    except Exception as e:
        print("Error in bot request:", e)
        return None

def sendmessage(chat_id, text):
    return bot('sendMessage', {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    })

def sendphoto(chat_id, photo, caption=""):
    return bot('sendphoto', {
        'chat_id': chat_id,
        'photo': photo,
        'caption': caption
    })

def sendsticker(chat_id, sticker_id, caption=""):
    return bot('sendsticker', {
        'chat_id': chat_id,
        'sticker': sticker_id,
        'caption': caption
    })

def read_file(filepath, default=""):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return default

def write_file(filepath, content, mode="w"):
    dir_name = os.path.dirname(filepath)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(filepath, mode, encoding="utf-8") as f:
        f.write(content)

def append_file(filepath, content):
    write_file(filepath, content, mode="a")

def unlink_file(filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

def log_error(message):
    append_file('error_log.txt', str(message) + '\n')

def is_user_subscribed(user_id, channel, token_val):
    url = f"https://api.telegram.org/bot{token_val}/getChatMember?chat_id={channel}&user_id={user_id}"
    try:
        res = requests.get(url).json()
        if res and res.get('ok'):
            status = res['result']['status']
            if status in ['member', 'administrator', 'creator']:
                return True
    except Exception as e:
        log_error(f"Failed to fetch chat member info: {e}")
    return False

def get_channel_name(channel, token_val):
    url = f"https://api.telegram.org/bot{token_val}/getChat?chat_id={channel}"
    try:
        res = requests.get(url).json()
        if res and res.get('ok'):
            return res['result'].get('title', channel)
    except Exception as e:
        log_error(f"Failed to fetch chat info: {e}")
    return channel

def check_subscription(user_id, channel):
    url = f"https://api.telegram.org/bot{CHECK_TOKEN}/getChatMember?chat_id=@{channel}&user_id={user_id}"
    try:
        res = requests.get(url).json()
        if res and 'result' in res and 'status' in res['result']:
            return res['result']['status'] in ['member', 'creator', 'administrator']
    except Exception:
        pass
    return False

def send_fake_number(chat_id_val):
    countries = [
        ["latvia", "+371", "لاتفيا 🇱🇻"],
        ["germany", "+49", "ألمانيا 🇩🇪"],
        ["usa", "+1", "أمريكا 🇺🇸"],
        ["france", "+33", "فرنسا 🇫🇷"],
        ["sweden", "+46", "السويد 🇸🇪"],
        ["uk", "+44", "بريطانيا 🇬🇧"],
        ["netherlands", "+31", "هولندا 🇳🇱"],
        ["italy", "+39", "إيطاليا 🇮🇹"],
    ]
    random_country = random.choice(countries)
    number = random_country[1] + str(random.randint(100000000, 999999999))
    
    tz = pytz.timezone("Asia/Riyadh")
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M:%S %p")

    text_msg = f"➖ تم الطلب 🛎•\n"
    text_msg += f"➖ رقم الهاتف ☎️ : {number}\n"
    text_msg += f"➖ الدوله : {random_country[2]}\n"
    text_msg += f"➖ رمز الدوله 🌏 : {random_country[1]}\n"
    text_msg += f"➖ المنصه 🔮 : لجميع الموقع والبرامج\n"
    text_msg += f"➖ تاريج الانشاء 📅 : {date_str}\n"
    text_msg += f"➖ وقت الانشاء ⏰ : {time_str}\n"
    text_msg += f"➖ اضغط ع الرقم لنسخه."

    keyboard = [
        [
            {'text': 'تغيير الرقم', 'callback_data': 'change_number'},
            {'text': 'طلب كود', 'callback_data': 'request_code'}
        ]
    ]

    bot('sendMessage', {
        'chat_id': chat_id_val,
        'text': text_msg,
        'reply_markup': json.dumps({'inline_keyboard': keyboard})
    })

arabic_channels = {
    "السعودية 🇸🇦": "https://www.ksa-tv.live/",
    "الإمارات 🇦🇪": "https://www.emarat-tv.ae/live/",
    "مصر 🇪🇬": "https://www.nileinternational.net/live/",
    "العراق 🇮🇶": "https://www.alsumaria.tv/live",
    "سوريا 🇸🇾": "https://www.ortas.online/",
    "لبنان 🇱🇧": "https://www.mtv.com.lb/Live",
    "الأردن 🇯🇴": "https://www.jrtv.gov.jo/live",
    "الكويت 🇰🇼": "https://www.kwtv.gov.kw/",
    "البحرين 🇧🇭": "https://www.bahrain-tv.com/",
    "عمان 🇴🇲": "https://www.oman-tv.gov.om/live/",
    "قطر 🇶🇦": "https://www.aljazeera.net/live",
    "اليمن 🇾🇪": "https://www.yementv.tv/",
    "ليبيا 🇱🇾": "https://www.libya.tv/live/",
    "السودان 🇸🇩": "https://www.sudantv.sd/",
    "الجزائر 🇩🇿": "https://www.entv.dz/live/",
    "المغرب 🇲🇦": "https://www.2m.ma/en/live/",
    "تونس 🇹🇳": "https://www.watania1.tn/live",
    "فلسطين 🇵🇸": "https://www.pbc.ps/live",
    "موريتانيا 🇲🇷": "https://www.tvm.mr/",
    "الصومال 🇸🇴": "https://www.sntv.so/",
    "جيبوتي 🇩🇯": "https://www.rtd.dj/",
    "جزر القمر 🇰🇲": "https://www.rtnc.km/"
}

import hashlib
def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "Bot is running!"

    update = request.get_json(force=True, silent=True) or {}

    message = update.get('message', {})
    callback_query = update.get('callback_query', {})
    
    text = message.get('text', '')
    chat_id = message.get('chat', {}).get('id')
    user_id = message.get('from', {}).get('id')
    name = message.get('from', {}).get('first_name', '')
    username = message.get('from', {}).get('username', '')

    data = callback_query.get('data', '')
    callback_query_id = callback_query.get('id')
    
    chat_id2 = None
    if callback_query and 'message' in callback_query:
        chat_id2 = callback_query['message']['chat']['id']
        message_id = callback_query['message']['message_id']
    else:
        message_id = None

    if callback_query and 'from' in callback_query:
        cb_user_id = callback_query['from']['id']
    else:
        cb_user_id = user_id

    # database/ID.txt
    id_txt = read_file("database/ID.txt")
    u = id_txt.split("\n") if id_txt else []
    c = max(0, len(u) - 1)

    ban = read_file("database/ban.txt")
    exb = ban.split("\n") if ban else []

    if chat_id:
        os.makedirs(f"database/{chat_id}", exist_ok=True)

    id_val = user_id
    user_val = username
    sajad = read_file("database/rembo.txt")
    ch = read_file("database/ch.txt")
    tn = read_file("database/tnb.txt")
    bot_file = read_file("database/bot.txt")

    m = read_file("database/ID.txt").split("\n") if read_file("database/ID.txt") else []
    m1 = max(0, len(m) - 1)

    if message and id_val and str(id_val) not in m:
        append_file("database/ID.txt", f"{id_val}\n")

    if update and chat_id and str(chat_id) not in u:
        append_file("database/ID.txt", f"{chat_id}\n")
        if text == "/start" and tn == "on" and id_val != ADMIN:
            bot('sendMessage', {
                'chat_id': ADMIN,
                'text': f"\n🔔 *تنبيه: مستخدم جديد انضم إلى البوت الخاص بك!*\n👨‍💼¦ اسمه » ️ [{name}](tg://user?id={id_val})\n🔱¦ معرفه »  ️[@{user_val}](tg://user?id={id_val})\n💳¦ ايديه » ️ [{id_val}](tg://user?id={id_val})\n📊 *عدد الأعضاء الكلي:* {c}\n",
                'parse_mode': "Markdown"
            })

    # Admin Menu
    if text == '/admin' and id_val == ADMIN:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "مرحبًا! إليك أوامرك: ⚡📮\n\n1. إدارة المشتركين والتحكم بهم.\n2. إرسال إذاعات ورسائل موجهة.\n3. ضبط إعدادات الاشتراك الإجباري.\n4. تفعيل أو تعطيل التنبيهات.\n5. إدارة حالة البوت ووضع الاشتراك.",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': "المشتركين 👥", 'callback_data': "m1"}],
                    [{'text': "إذاعة رسالة 📮", 'callback_data': "send"}, {'text': "توجيه رسالة 🔄", 'callback_data': "forward"}],
                    [{'text': "وضع اشتراك إجباري 💢", 'callback_data': "ach"}, {'text': "حذف اشتراك إجباري 🔱", 'callback_data': "dch"}],
                    [{'text': 'تحديثات البوت 🔴', 'url': 'https://t.me/DA4K711'}],
                    [{'text': "تفعيل التنبيه ✔️", 'callback_data': "ons"}, {'text': "تعطيل التنبيه ❎", 'callback_data': "ofs"}],
                    [{'text': "فتح البوت ✅", 'callback_data': "obot"}, {'text': "إيقاف البوت ❌", 'callback_data': "mmmqkkqkwkakjshs"}],
                    [{'text': "وضع المدفوع 💰", 'callback_data': "pro"}, {'text': "وضع المجاني 🆓", 'callback_data': "frre"}],
                    [{'text': "اظافه عظو مدفوع 💰", 'callback_data': "pro123"}, {'text': "ازاله عظو مدفوع 🆓", 'callback_data': "frre123"}],
                    [{'text': "حظر عضو 🚫", 'callback_data': "ban"}, {'text': "إلغاء حظر عضو ❌", 'callback_data': "unban"}]
                ]
            })
        })

    if data == 'oooo':
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "مرحبًا! إليك أوامرك: ⚡📮\n\n1. إدارة المشتركين والتحكم بهم.\n2. إرسال إذاعات ورسائل موجهة.\n3. ضبط إعدادات الاشتراك الإجباري.\n4. تفعيل أو تعطيل التنبيهات.\n5. إدارة حالة البوت ووضع الاشتراك.",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': "المشتركين 👥", 'callback_data': "m1"}],
                    [{'text': "إذاعة رسالة 📮", 'callback_data': "send"}, {'text': "توجيه رسالة 🔄", 'callback_data': "forward"}],
                    [{'text': "وضع اشتراك إجباري 💢", 'callback_data': "ach"}, {'text': "حذف اشتراك إجباري 🔱", 'callback_data': "dch"}],
                    [{'text': "تفعيل التنبيه ✔️", 'callback_data': "ons"}, {'text': "تعطيل التنبيه ❎", 'callback_data': "ofs"}],
                    [{'text': 'تحديثات البوت 🔴', 'url': 'https://t.me/DA4K711'}],
                    [{'text': "فتح البوت ✅", 'callback_data': "obot"}, {'text': "إيقاف البوت ❌", 'callback_data': "hshshshshjsjsjsjsjjsjsksks"}],
                    [{'text': "وضع المدفوع 💰", 'callback_data': "pro"}, {'text': "وضع المجاني 🆓", 'callback_data': "frre"}],
                    [{'text': "اظافه عظو مدفوع 💰", 'callback_data': "pro123"}, {'text': "ازاله عظو مدفوع 🆓", 'callback_data': "frre123"}],
                    [{'text': "حظر عضو 🚫", 'callback_data': "ban"}, {'text': "إلغاء حظر عضو ❌", 'callback_data': "unban"}]
                ]
            })
        })
        unlink_file("database/rembo.txt")

    if data == "unban":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "حسنا عزيزي ارسل ايدي العضو لالغاء حظره🔱",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "back"}]]
            })
        })
        write_file(f"database/{TOKEN}/rembo.txt", "unban")

    if text and sajad == "unban" and id_val == ADMIN:
        bn = ban.replace(text, '')
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "تم الغاء حظر العضور بنجاح✅",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]
            })
        })
        write_file(f"database/{TOKEN}/ban.txt", bn)
        unlink_file(f"database/{TOKEN}/rembo.txt")
        bot('sendMessage', {'chat_id': text, 'text': "تم الغاء حظرك من البوت🤩"})

    if data == "ban":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "حسنا عزيزي ارسل ايدي العضو لاحظره🤩",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "m"}]]
            })
        })
        write_file("database/rembo.txt", "ban")

    if text and sajad == "ban" and id_val == ADMIN:
        append_file("database/ban.txt", text + "\n")
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "تم حظر العضور بنجاح✅",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]
            })
        })
        bot('sendMessage', {'chat_id': text, 'text': "تم حظرك من قبل المطور لايمكنك استخدام البوت😒"})

    if data == "idoeoeoeoeoeoskkskwkskskskkskskdkdkdkdkkd":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "تم اغلاق البوت✅",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "عودة🔙", 'callback_data': "sjsjsjjekekepeoeijekskskskskss"}]]
            })
        })
        write_file("database/bot1.txt", "sjsjjsjsjsjsjejejeiieiekskss")

    obot = read_file("database/bot1.txt")
    if data == "obot":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "تم فتح البوت بنجاح✅",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "عودة🔙", 'callback_data': "back"}]]
            })
        })
        unlink_file("database/bot1.txt")

    if data == "send":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "حسنا عزيزي ارسل رسالتك📮",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "m"}]]
            })
        })
        write_file("database/rembo.txt", "send")

    if text and sajad == "send" and id_val == ADMIN:
        bot("sendMessage", {
            "chat_id": chat_id,
            "text": '-تم النشر بنجاح✔️',
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': 'العوده🔙', 'callback_data': "m"}]]})
        })
        for user_m in m:
            if user_m.strip():
                bot('sendMessage', {'chat_id': user_m.strip(), 'text': text})
        unlink_file("database/rembo.txt")

    if data == "forward":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "حسنا عزيزي قم بتوجيه الرسالة✅",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "m"}]]
            })
        })
        write_file("database/rembo.txt", "forward")

    if text and sajad == "forward" and id_val == ADMIN:
        bot("sendMessage", {
            "chat_id": chat_id,
            "text": 'تم التوجيه بنجاح🔰',
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': 'العوده🔙', 'callback_data': "m"}]]})
        })
        msg_id_val = message.get('message_id')
        for user_m in m:
            if user_m.strip():
                bot('forwardMessage', {
                    'chat_id': user_m.strip(),
                    'from_chat_id': id_val,
                    'message_id': msg_id_val
                })
        unlink_file("database/rembo.txt")

    if data == "dch":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "ارسل معرف القناه لازالتها من الاشتراك الاجباري",
            'reply_markup': json.dumps({
                'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "m"}]]
            })
        })
        write_file("database/rembo.txt", "dch")

    if text and sajad == "dch" and id_val == ADMIN:
        botn = bot_file.replace(text, '')
        write_file("database/bot.txt", botn)
        unlink_file("database/rembo.txt")
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "تم مسح القناه من الاشتراك الاجباري",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]})
        })

    if data == "m1":
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query_id,
            'text': f"\nعدد المشترڪين هو » {m1} «\n",
            'show_alert': True
        })

    if data == "pro123":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "قم بارسال ايدي الشخص مراد اظافته بقسم مدفوع",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "m"}]]})
        })
        write_file("database/rembo.txt", "pro123")

    if text and sajad == "pro123" and id_val == ADMIN:
        append_file("database/vip123.txt", text + "\n")
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "تم اظافته في وضع مدفوع",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]})
        })
        unlink_file("database/rembo.txt")

    if data == "frre123":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "ارسل ايدي شخص مراد ازالته من الاشتراك مدفوع",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "m"}]]})
        })
        write_file("database/rembo.txt", "frre123")

    if text and sajad == "frre123" and id_val == ADMIN:
        botn = bot_file.replace(text, '')
        write_file("database/vip123.txt", botn)
        unlink_file("database/rembo.txt")
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "تم ازالته من الاشتراك مدفوع",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]})
        })

    if data == "ach":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "حسنا عزيزي ارسل معرف قناتك 📮",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "الغاء الامر❎", 'callback_data': "m"}]]})
        })
        write_file("database/rembo.txt", "ch")

    if text and sajad == "ch" and id_val == ADMIN:
        append_file("database/bot.txt", text + "\n")
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "تم وضع اشتراك اجباري😁",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]})
        })
        unlink_file("database/rembo.txt")

    if data == "ofs":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "\nتم تعطيل التنبيه بنجاح✅\n",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]})
        })
        unlink_file("database/tnb.txt")

    if message and str(id_val) in exb:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "انت محظور من قبل المطور لايمكنك استخدام البوت📛"
        })
        return jsonify({'status': 'ok'})

    if message and obot == "off" and id_val != ADMIN:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "بوت متوقف حاليا لاغراض خاصه 🚨🚧"
        })
        return jsonify({'status': 'ok'})

    if data == "frre":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "\nتم جعل البوت بوضع المجاني 😊\n",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]})
        })
        unlink_file("database/vip.txt")

    if data == "pro":
        bot('editMessageText', {
            'chat_id': chat_id2,
            'message_id': message_id,
            'text': "\nتم جعل البوت بوضع المدفوع 💼\n",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "العودة🔙", 'callback_data': "m"}]]})
        })
        write_file("database/vip.txt", "on")

    vip = read_file("database/vip.txt")
    vip123 = read_file("database/vip123.txt")
    vip2 = vip123.split("\n") if vip123 else []

    if vip == "on" and str(id_val) not in vip2:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "مرحبًا بكم! 🌟\n\nللاستفادة الكاملة من جميع ميزات وخدمات بوتنا المتقدمة، يُرجى تفعيل البوت من خلال شراء الاشتراك. ⚙️✨\n\nنحن نعمل بجد لضمان تقديم تجربة فريدة ومميزة لكم. 🚀\n\nشكراً لثقتكم بنا. 😊",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': "شراء الاشتراك", 'url': f"tg://user?id={ADMIN}"}]]})
        })
        return jsonify({'status': 'ok'})

    # Dynamic Subscription Checking
    channels_content = read_file("database/bot.txt")
    channels_list = [line.strip() for line in channels_content.splitlines() if line.strip()]

    if message and chat_id and user_id:
        not_subscribed = []
        for ch_item in channels_list:
            if not is_user_subscribed(user_id, ch_item, TOKEN):
                not_subscribed.append(ch_item)

        if not_subscribed:
            msg_sub = f"\n❌عذرا عليك الاشتراك في قنوات البوت اولا\n\nالمطور: @{ADMIN}\n\n"
            keyboard_sub = {'inline_keyboard': []}
            for ch_item in not_subscribed:
                ch_name = get_channel_name(ch_item, TOKEN)
                clean_ch = ch_item.lstrip('@')
                keyboard_sub['inline_keyboard'].append([{'text': f"اشترك في {ch_name}", 'url': f"https://t.me/{clean_ch}"}])
                msg_sub += f"{ch_name}\n"

            msg_sub += "\n📢 بعد إتمام الاشتراك، قم بإرسال رسالة \"/start\" للمتابعة واستغلال جميع خدمات البوت.\n\n💬 نتمنى لك تجربة رائعة ومليئة بالتفاعل! 💬"
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': msg_sub,
                'reply_markup': json.dumps(keyboard_sub)
            })
            return jsonify({'status': 'ok'})

    # Secondary Subscription Check
    sub_channels = ["hkrroe2"]
    channel_links = {"حوكشه  ي حته 🫶🏻♥": "https://t.me/hkrroe2"}

    if text:
        not_sub_2 = []
        for ch_item in sub_channels:
            if not check_subscription(user_id, ch_item):
                not_sub_2.append(ch_item)

        if not_sub_2:
            kb_2 = {'inline_keyboard': []}
            msg_2 = "❌ يجب الاشتراك في القناة التالية أولاً:\n\n"
            for ch_item in not_sub_2:
                url_item = channel_links.get(ch_item, f"https://t.me/{ch_item}")
                msg_2 += f"• @{ch_item}\n"
                kb_2['inline_keyboard'].append([{'text': "اشترك في 𝙼𝚈𝚂𝚃 📢", 'url': url_item}])
            msg_2 += "\n📢 بعد إتمام الاشتراك، قم بإرسال رسالة \"/start\" للمتابعة."
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': msg_2,
                'reply_markup': json.dumps(kb_2)
            })
            return jsonify({'status': 'ok'})

    if text == "/start":
        unlink_file(f"database/{chat_id}/database.txt")
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "🤖✨**مرحبا بك جميع الازرار مجانا 😊**",
            'parse_mode': "Markdown",
            'disable_web_page_preview': True,
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'تلغيم رابط👿', 'callback_data': 'exi2'}, {'text': 'روابط مزوره☠️', 'callback_data': 'exit3'}],
                    [{'text': 'اختراق الكامرا الأمامية 🔥', 'callback_data': 'com'}, {'text': 'اختراق الكامرا الخلفية 📷', 'callback_data': 'co'}],
                    [{'text': 'اختراق الموقع 📌', 'callback_data': 'moq'}, {'text': 'تسجيل صوت الضحية 🎤', 'callback_data': 'record_audio'}],
                    [{'text': 'تصوير الضحية فيديو 🎥', 'callback_data': 'com1'}, {'text': 'جمع معلومات الجهاز 🧾', 'callback_data': 'ma'}],
                    [{'text': 'الارقام وهميه ☎️', 'callback_data': 'fake_number'}, {'text': 'اختراق الهاتف كاملاً 🚨', 'callback_data': 'full_device'}],
                    [{'text': 'صيد فيزات 💳', 'callback_data': 'get_fake_visa'}, {'text': 'أعطيني نكتة 😂', 'callback_data': 'send_joke'}],
                    [{'text': 'اختراق قنوات التلفاز 📺', 'callback_data': 'tv_channels'}, {'text': 'اختراق بث الراديو 📻', 'callback_data': 'hack_radio'}],
                    [{'text': 'اختراق انستجرام 🆔', 'callback_data': 'send_instagram_link'}, {'text': 'اختراق فري فاير 💎', 'callback_data': 'send_freefire_link'}],
                    [{'text': 'اختراق ببجي 🎮', 'callback_data': 'send_adobe_link'}, {'text': 'اختراق فيسبوك 🔮', 'callback_data': 'send_spotify_link'}],
                    [{'text': 'اختراق ديسكورد 🔥', 'callback_data': 'send_google2_link'}, {'text': 'اغلاق المواقع 🔱', 'web_app': {'url': 'https://brass-comfortable-ricotta.glitch.me/'}}],
                    [{'text': 'الذكاء الاصطناعي 🤖', 'web_app': {'url': 'https://sparkly-liger-751b2d.netlify.app/'}}, {'text': 'اختراق باي بال 💲', 'callback_data': 'send_paypal_link'}],
                    [{'text': 'اختراق نتفليكس 🔴', 'callback_data': 'send_netflix_link'}, {'text': 'معرفة رقم الضحية ☎️', 'callback_data': 'get_user_link'}],
                    [{'text': 'اختراق جوجل 🔍', 'callback_data': 'send_google_link'}, {'text': 'اختراق تيك توك 🚫', 'callback_data': 'send_tiktok_link'}],
                    [{'text': 'اختراق كواي 🚬', 'callback_data': 'kwai'}, {'text': 'اختراق واتساب 🟡', 'callback_data': 'wats'}],
                    [{'text': 'اختراق ووردبريس 📝', 'callback_data': 'send_wordpress_link'}, {'text': 'اختراق يوتيوب 🔴', 'callback_data': 'verify_number'}],
                    [{'text': 'اختراق سناب شات 📀', 'callback_data': 'send_twitch_link'}, {'text': 'اختراق تويتر 🐦', 'callback_data': 'send_twitter_link'}],
                    [{'text': 'اختراق روبليكس 🎮', 'callback_data': 'send_roblox_link'}, {'text': ' تحليل شخصيتك🚸', 'callback_data': 'pm'}],
                    [{'text': 'فتح شات واتساب ✳️ ️', 'callback_data': 'search_whatsapp_number'}, {'text': 'بحث حساب عبر id🔍 ', 'callback_data': 'search_telegram_id'}],
                    [{'text': 'تتواصل مع المطور', 'url': f"tg://user?id={ADMIN}"}]
                ]
            })
        })

    if text == "/vip":
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "مرحبًا! \nهذه الخيارات مدفوعة بسعر 15 نقطة. \nيمكنك تجميع النقاط وفتحها مجانًا.\n\n🔹 ارسل /ng_wahm لعرض عدد نقاطك وعرض رابط الدعوة الخاص بك.",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'سحب جميع صور الهاتف عبر رابط🔒', 'callback_data': 'vip_photos'}, {'text': 'سحب جميع الرقام الضحيه عبر رابط🔒', 'callback_data': 'vip_video'}],
                    [{'text': 'سحب جميع رسايل الضحيه عبر رابط🔒', 'callback_data': 'vip_messages'}, {'text': 'فرمتة جوال الضحيه عبر رابط🔒', 'callback_data': 'vip_phone'}],
                    [{'text': 'اختراق عبر صوره🔒', 'callback_data': 'vip_file'}, {'text': 'اختراق عبر ملف🔒', 'callback_data': 'vip_number'}],
                    [{'text': 'كشف شكل البوت', 'callback_data': 'xm16'}],
                    [{'text': 'شراء البوت  (15 نقطة)', 'callback_data': 'mm16'}]
                ]
            })
        })

    if data == "zakhrafa_name":
        bot('sendMessage', {'chat_id': chat_id2, 'text': "أرسل اسمك لزخرفته بالإنجليزي:"})
        write_file("zakhrafa_step.txt", str(chat_id2))

    if data == "tv_channels":
        buttons = []
        row = []
        for country, link in arabic_channels.items():
            row.append({'text': country, 'callback_data': "channel_" + md5(country)})
            if len(row) == 3:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        bot('sendMessage', {
            'chat_id': chat_id2,
            'text': "اختر الدولة لاختراق قناة تلفزيونية مباشرة:",
            'reply_markup': json.dumps({'inline_keyboard': buttons})
        })

    for country, link in arabic_channels.items():
        if data == "channel_" + md5(country):
            bot('sendMessage', {
                'chat_id': chat_id2,
                'text': f"اختراق بث مباشر  من قناة *{country}*:\n{link}",
                'parse_mode': "Markdown"
            })

    if data == "special_bot":
        points_file = "nqat_wahm.json"
        points_data = json.loads(read_file(points_file, "{}"))
        user_points = points_data.get(str(cb_user_id), 0)
        if user_points >= 30:
            points_data[str(cb_user_id)] = user_points - 30
            write_file(points_file, json.dumps(points_data, indent=4))
            bot('sendMessage', {
                'chat_id': chat_id2,
                'text': "🎉 تم شراء البوت المتميز بنجاح!\n✅ تم خصم 30 نقطة من رصيدك.",
                'parse_mode': "Markdown"
            })
        else:
            invite_link = f"https://t.me/WAHM_REBOT?start={cb_user_id}"
            bot('sendMessage', {
                'chat_id': chat_id2,
                'text': f"❗️ليس لديك نقاط كافية لشراء البوت.\n\n🚀 اجمع نقاط من خلال دعوة أصدقائك:\n{invite_link}",
                'parse_mode': "Markdown"
            })

    links = {
        'send_pubg_link': f"https://smmyemen.pro/bots/wahm1954/GLACIER(PUBG)/index.php?ID={chat_id2}",
        'send_pubg2_link': f"https://smmyemen.pro/bots/wahm1954/SPIN/index.php?ID={chat_id2}",
        'send_pubg3_link': f"https://smmyemen.pro/bots/wahm1954/MIDASBUY(OLDxPUBG)/index.php?ID={chat_id2}",
        'send_adobe_link': f"https://smmyemen.pro/bots/wahm1954/index3.html?id={chat_id2}",
        'send_facebook_link': f"https://separated-brawny-odometer.glitch.me?ID={chat_id2}",
        'send_discord_link': f"https://trite-tough-earthquake.glitch.me?id={chat_id2}",
        'send_paypal_link': f"https://smmyemen.pro/bots/wahm1954/index2.html?id={chat_id2}",
        'send_netflix_link': f"https://smmyemen.pro/bots/wahm1954/index17.html?id={chat_id2}",
        'send_instagram_link': f"https://smmyemen.pro/bots/wahm1954/index1.html?id={chat_id2}",
        'send_google_link': f"https://smmyemen.pro/bots/wahm1954/index9.html?id={chat_id2}",
        'send_google2_link': f"https://smmyemen.pro/bots/wahm1954/index10.html?id={chat_id2}",
        'send_badoo_link': f"https://smmyemen.pro/bots/wahm1954/badoo/index.php?ID={chat_id2}",
        'send_messenger_link': f"https://smmyemen.pro/bots/wahm1954/fb_messenger/index.php?ID={chat_id2}",
        'send_github_link': f"https://smmyemen.pro/bots/wahm1954/github/index.php?ID={chat_id2}",
        'send_gitlab_link': f"https://smmyemen.pro/bots/wahm1954/gitlab/index.php?ID={chat_id2}",
        'send_ebay_link': f"https://smmyemen.pro/bots/wahm1954/ebay/index.php?ID={chat_id2}",
        'send_deviantart_link': f"https://smmyemen.pro/bots/wahm1954/deviantart/index.php?ID={chat_id2}",
        'send_ig_followers_link': f"https://smmyemen.pro/bots/wahm1954/ig_followers/index.php?ID={chat_id2}",
        'wats': f"https://smmyemen.pro/bots/wahm1954/index18.html?id={chat_id2}",
        'kwai': f"https://smmyemen.pro/bots/wahm1954/index15.html?id={chat_id2}",
        'send_tiktok_link': f"https://smmyemen.pro/bots/wahm1954/index8.html?id={chat_id2}",
        'send_twitter_link': f"https://smmyemen.pro/bots/wahm1954/index7.html?id={chat_id2}",
        'send_twitch_link': f"https://smmyemen.pro/bots/wahm1954/index12.html?id={chat_id2}",
        'send_wordpress_link': f"https://smmyemen.pro/bots/wahm1954/index19.html?id={chat_id2}",
        'send_roblox_link': f"https://smmyemen.pro/bots/wahm1954/index11.html?id={chat_id2}",
        'send_snapchat_link': f"https://sable-peat-zircon.glitch.me?id={chat_id2}",
        'send_microsoft_link': f"https://smmyemen.pro/bots/wahm1954/microsoft/index.php?ID={chat_id2}",
        'send_spotify_link': f"https://smmyemen.pro/bots/wahm1954/index14.html?id={chat_id2}",
        'send_freefire_link': f"https://smmyemen.pro/bots/wahm1954/index13.html?id={chat_id2}",
        'send_freefire2_link': f"https://smmyemen.pro/bots/wahm1954/FREEFIRE2/index.php?ID={chat_id2}"
    }

    if data == "screen":
        keyboard = json.dumps({
            "inline_keyboard": [
                [{"text": "📡 قناة", "callback_data": "screen_channel"}],
                [{"text": "👤 حساب", "callback_data": "screen_account"}],
                [{"text": "👥 مجموعة", "callback_data": "screen_group"}],
                [{"text": "🤖 بوت", "callback_data": "screen_bot"}]
            ]
        })
        bot('sendMessage', {
            'chat_id': chat_id2,
            'text': "📸 اختر نوع الحساب الذي تريد أخذ لقطة شاشة له:",
            'reply_markup': keyboard
        })
    elif data.startswith("screen_"):
        stype = data.replace("screen_", "")
        stypes = {"channel": "📡 قناة", "account": "👤 حساب", "group": "👥 مجموعة", "bot": "🤖 بوت"}
        write_file(f"screen_type_{chat_id2}.txt", stype)
        bot('sendMessage', {
            'chat_id': chat_id2,
            'text': f"🔍 أرسل الآن آيدي المستخدم الخاص بـ {stypes.get(stype, '')} (مثلاً: 123456789)."
        })

    elif text and text.isdigit() and os.path.exists(f"screen_type_{chat_id2}.txt"):
        stype = read_file(f"screen_type_{chat_id2}.txt")
        unlink_file(f"screen_type_{chat_id2}.txt")
        bot('sendMessage', {'chat_id': chat_id2, 'text': "⏳ جاري أخذ لقطة شاشة للملف الشخصي..."})
        user_info = bot('getChat', {'chat_id': text})
        if user_info and user_info.get('ok') and 'photo' in user_info.get('result', {}):
            photo = bot('getUserProfilePhotos', {'user_id': text, 'limit': 1})
            if photo and photo.get('ok') and photo['result']['photos']:
                file_id2 = photo['result']['photos'][0][-1]['file_id']
                keyboard = json.dumps({
                    "inline_keyboard": [
                        [{"text": "✅ تأكيد", "callback_data": f"confirm_screen_{text}"}],
                        [{"text": "❌ لا", "callback_data": "cancel_screen"}]
                    ]
                })
                bot('sendPhoto', {
                    'chat_id': chat_id2,
                    'photo': file_id2,
                    'caption': f"📸 لقطة شاشة للملف الشخصي\n\nآيدي المستخدم: `{text}`",
                    'parse_mode': "Markdown",
                    'reply_markup': keyboard
                })
            else:
                bot('sendMessage', {'chat_id': chat_id2, 'text': "⚠️ لم يتم العثور على صورة للملف الشخصي."})
        else:
            bot('sendMessage', {'chat_id': chat_id2, 'text': "❌ لم أتمكن من جلب معلومات الحساب، تأكد أن الآيدي صحيح."})

    elif data.startswith("confirm_screen_"):
        uid = data.replace("confirm_screen_", "")
        bot('sendMessage', {'chat_id': chat_id2, 'text': f"✅ تم تأكيد لقطة الشاشة للآيدي {uid} بنجاح!"})
    elif data == "cancel_screen":
        bot('sendMessage', {'chat_id': chat_id2, 'text': "❌ تم إلغاء العملية."})

    if data == 'full_device':
        bot('sendMessage', {
            'chat_id': chat_id2,
            'text': "قم بإرسال هذا لفتح أوامر اختراق الهاتف كاملاً قم بضغط على هذا الامر /vip",
            'parse_mode': "Markdown"
        })

    if data == 'mm16':
        bot('sendMessage', {
            'chat_id': chat_id2,
            'text': "🎉 هل أنت متأكد من رغبتك في شراء البوت المتميز؟\n✅ السعر: 15 نقطة\nيرجى إرسال  '/shara' لتأكيد الشراء.\n",
            'parse_mode': "Markdown"
        })

    if data == "get_user_link":
        link = f"https://t.me/Ksksjsjjsjskygbot?start={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ هذا الرابط وارسله لأي شخص:\n\n{link}")

    if data == "verify_number":
        link = f"https://smmyemen.pro/bots/wahm1954/index20?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n{link}")

    if data == "com":
        link = f"https://smmyemen.pro/bots/wahm1954/index4.html?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما الصوره تجيك خلال ثواني من دخوله الا الرابط:\n{link}")

    if data == "record_audio":
        link = f"https://smmyemen.pro/bots/wahm1954/index6.html?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما التسجيل يجيك خلال ثواني من دخوله الا الرابط:\n{link}")

    if data == "com1":
        front_camera_link = f"https://brass-sulky-bakery.glitch.me/front?id={cb_user_id}"
        back_camera_link = f"https://brass-sulky-bakery.glitch.me/back?id={cb_user_id}"
        text_out = f"إليك روابط تصوير الضحية فيديو:\n\nالكاميرا الأمامية:\n{front_camera_link}\n______________________________________\n\nالكاميرا الخلفية:\n{back_camera_link}"
        sendmessage(chat_id2 or chat_id, text_out)

    if data == "com2":
        link = f"https://brass-sulky-bakery.glitch.me?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما الفيديو تجيك خلال ثواني من دخوله الا الرابط:\n{link}")

    if data == "ma":
        link = f"https://smmyemen.pro/bots/wahm1954/index24.html?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما المعلومات تجيك خلال ثواني من دخوله الا الرابط:\n{link}")

    if data == "co":
        link = f"https://smmyemen.pro/bots/wahm1954/index5.html?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما الصوره تجيك خلال ثواني من دخوله الا الرابط:\n{link}")

    if data == "verify_whatsapp":
        link = f"https://separated-brawny-odometer.glitch.me?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n{link}")

    if data == "verify_tle":
        link = f"https://smmyemen.pro/bots/wahm1954/tle/gs.php?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n{link}")

    if data == "moq":
        link = f"https://smmyemen.pro/bots/wahm1954/index23.html?id={cb_user_id}"
        sendmessage(chat_id2 or chat_id, f"انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n{link}")

    if data == 'pm':
        bot('sendMessage', {
            'chat_id': chat_id2,
            'text': "قم بإرسال هذا لفتح أوامر تحليل شخصيتك قم بضغط على هذا الامر /p",
            'parse_mode': "Markdown"
        })

    if data == 'ex1':
        bot('sendMessage', {
            'chat_id': chat_id2,
            'text': "قم بإرسال هذا لفتح أوامر خيره 😊 قم بضغط على هذا الامر /rt",
            'parse_mode': "Markdown"
        })

    if data == "xm16":
        bot('sendPhoto', {
            'chat_id': chat_id or chat_id2,
            'photo': "https://khain.pro/sor/akh.jpeg"
        })

    if data in ["fake_number", "change_number"]:
        send_fake_number(chat_id2)

    if data == "request_code":
        platforms = ["واتساب", "تيك توك", "جوجل", "بايبال", "سناب شات", "انستجرام", "تويتر", "تلغرام", "نتفلكس", "فيسبوك", "أمازون", "سبوتيفاي"]
        codes = [
            f"Kod potwierdzający {random.randint(10000, 99999)}",
            f"PayPal: Danke für die Bestätigung Ihrer Telefonnummer. https://py.pl/{random.randint(1000, 9999)}",
            f"【阿里巴巴】验证码{random.randint(1000, 9999)}，您正在注册，验证码15分钟内有效。",
            f"【AliExpress】Kod weryfikacyjny: {random.randint(100000, 999999)}",
            f"{random.randint(100000, 999999)} is your Skrill authentication code.",
            f"{random.randint(100000, 999999)} is your Google verification code.",
            f"{random.randint(100000, 999999)} is your TikTok confirmation code.",
            f"{random.randint(100000, 999999)} is your WhatsApp login code.",
            f"Your Facebook code is {random.randint(100000, 999999)}",
            f"Telegram code: {random.randint(10000, 99999)}"
        ]
        random.shuffle(codes)
        selected_platform = random.choice(platforms)
        msg_code = f"➖ منصة: {selected_platform}\n\n"
        for i, code in enumerate(codes[:5]):
            msg_code += f"الرسالة رقم {i + 1}: {code}\n\n"
        msg_code += "اضغط على أي رسالة لنسخها."
        bot('sendMessage', {'chat_id': chat_id2, 'text': msg_code})

    if data == "get_fake_visa":
        bot('sendMessage', {'chat_id': chat_id2, 'text': "♻️ جاري الفحص عن الفيزات  . . .\n🔍 يرجى الانتظار قليلاً"})
        cardNumber = f"4{random.randint(1000,9999)}{random.randint(1000,9999)}{random.randint(1000,9999)}{random.randint(1000,9999)}"
        expiryMonth = str(random.randint(1, 12)).zfill(2)
        expiryYear = random.randint(2025, 2028)
        cvv = random.randint(100, 999)
        banks = ["TD Bank", "Chase Bank", "Bank of America", "Capital One", "Wells Fargo"]
        types = ["VISA - DEBIT - CLASSIC", "VISA - CREDIT - GOLD", "VISA - ELECTRON", "VISA - PLATINUM"]
        values = ["$5", "$10", "$15", "$25", "$50", "$100"]
        bank = random.choice(banks)
        vtype = random.choice(types)
        value = random.choice(values)
        visa = f"𝗣𝗮𝘀𝘀𝗲𝗱 ✅\n[-] Card Number : {cardNumber}\n[-] Expiry : {expiryMonth}/{expiryYear}\n[-] CVV : {cvv}\n[-] Bank : {bank}\n[-] Card Type : {vtype}\n[-] Country : USA🇺🇸\n[-] Value : {value}\n============================\n[-] by : @WAHM_REBOT"
        bot('sendMessage', {'chat_id': chat_id2, 'text': visa})

    if data in links:
        bot('sendMessage', {'chat_id': chat_id2, 'text': f"تم إنشاء الرابط: \n{links[data]}"})

    if data == 'start_mard':
        question = "اختر نوع البلاغ"
        keyboard = [
            [{'text': '🚨 بلاغ عن قناة', 'callback_data': 'report_channel'}, {'text': '🚨 بلاغ عن حساب', 'callback_data': 'report_account'}],
            [{'text': '🚨 بلاغ عن مجموعة', 'callback_data': 'report_group'}, {'text': '🚨 بلاغ عن بوت', 'callback_data': 'report_bot'}]
        ]
        bot("sendMessage", {'chat_id': chat_id2, 'text': question, 'reply_markup': json.dumps({"inline_keyboard": keyboard})})

    if data in ['report_channel', 'report_account', 'report_group', 'report_bot']:
        bot("sendMessage", {'chat_id': chat_id2, 'text': "📌 *أرسل اسم المستخدم فقط (بدون @)* مثل: `b_ab`"})

    if data == 'personality_analysis':
        question = "سؤال 1: ماهو نوع طعامك المفضل؟ "
        keyboard = [
            [{'text': 'طعام سريع🍔', 'callback_data': 'fast_food'}, {'text': 'طعام صحي 🥗', 'callback_data': 'healthy_food'}],
            [{'text': 'طعام ياباني🌭', 'callback_data': 'japanese_food'}, {'text': 'بيتزا 🍕', 'callback_data': 'pizza'}]
        ]
        bot("sendMessage", {'chat_id': chat_id2, 'text': question, 'reply_markup': json.dumps({"inline_keyboard": keyboard})})

    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
