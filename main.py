import json
import signal
import sys

import telebot
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
from PIL import Image, ImageDraw, ImageFont
import time



TOKEN = "7826152623:AAGPlVwcScLDOo7LxC_xAUK24M0KSDttODY"
bot = telebot.TeleBot(TOKEN)
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
bot.timeout = 60

TEST_FILE = "test_savollari.json"
USERS_FILE = "users.json"

# Kanal usernamelari
CHANNELS = ["@WebKing_uz", "@Baliqchi_MMTB"]


def load_data(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


test_savollari = load_data(TEST_FILE)
users = load_data(USERS_FILE)


def check_subscription(user_id):
    """Foydalanuvchi barcha kanallarga a'zo bo'lganligini tekshiradi."""
    for channel in CHANNELS:
        try:
            chat_member = bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False  # Agar a'zo bo'lmasa
        except Exception as e:
            print(f"Xatolik: {e}")
            return False
    return True  # Agar barcha kanallarga a'zo bo'lsa


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    time.sleep(2)
    if not check_subscription(chat_id):
        # Agar foydalanuvchi a'zo bo'lmasa, unga kanallarga a'zo bo‘lishni so‘raymiz
        channels_list = "\n".join([f"👉 {channel}" for channel in CHANNELS])
        markup = InlineKeyboardMarkup()
        for channel in CHANNELS:
            btn = InlineKeyboardButton("🔗 Kanalga qo'shilish", url=f"https://t.me/{channel.replace('@', '')}")
            markup.add(btn)
        markup.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription"))

        bot.send_message(chat_id,
                         f"❌ Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:\n\n{channels_list}\n\n"
                         "✅ A'zo bo'lgach, *Tekshirish* tugmasini bosing!",
                         reply_markup=markup, parse_mode="Markdown")
        return

    # Foydalanuvchi allaqachon ro‘yxatdan o‘tgan bo‘lsa, menyuni yuboramiz
    user = next((u for u in users if u['id'] == chat_id), None)
    if user:
        send_main_menu(chat_id)
        return

    msg = bot.send_message(chat_id, "👋 Assalomu alaykum! Ismingizni va familiyangizni kiriting:")
    bot.register_next_step_handler(msg, get_address)


@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    """Tekshirish tugmachasi bosilganda ishlaydi."""
    chat_id = call.message.chat.id
    if check_subscription(chat_id):
        bot.send_message(chat_id, "✅ Siz barcha kanallarga a'zo bo‘lgansiz. Botdan foydalanishingiz mumkin!")
        start(call.message)  # Foydalanuvchini davom ettirish
    else:
        bot.answer_callback_query(call.id, "❌ Siz hali ham barcha kanallarga a'zo bo‘lmadingiz!")


# Sertifikat rasmini yuklash
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

certificate_pathbiznes = os.path.join(BASE_DIR, "photo_1_2025-03-16_02-04-31.jpg")
certificate_pathit = os.path.join(BASE_DIR, "photo_2_2025-03-16_02-04-31.jpg")
certificate_pathtil = os.path.join(BASE_DIR, "photo_4_2025-03-16_02-04-31.jpg")
certificate_pathtibbiyot = os.path.join(BASE_DIR, "photo_5_2025-03-16_02-04-31.jpg")
certificate_pathitharbiy = os.path.join(BASE_DIR, "photo_3_2025-03-16_02-04-31.jpg")


def get_address(message):
    chat_id = message.chat.id
    name = message.text.strip()

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    locations = ["Andijon shaxar", "Andijon tumani","Asaka tumani","", "Jarqo'rg'on tumani", "Baliqchi tumani" ,"Bo'ston tumani","Bulpqboshi tumani","Izbosgan tumani","Jallaquduq tumani","Marhamat tumani"," Oltinko'l tumani","Paxtaobot tumani","Qo'rg'ontepa tumani","Qo'rg'ontepa tumani","Shaxrixon tumani","Ulug'nor tumani", "Xo'jaobot tumani","Xonobot shaxar"]

    for location in locations:
        markup.add(KeyboardButton(location))

    msg = bot.send_message(chat_id, "🏠 Yashash manzilingizni tanlang:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_school, name)


def get_school(message, name):
    chat_id = message.chat.id
    address = message.text.strip()
    msg = bot.send_message(chat_id, "🏫 Qaysi maktabda o‘qiysiz?")
    bot.register_next_step_handler(msg, get_phone, name, address)


def get_phone(message, name, address):
    chat_id = message.chat.id
    school = message.text.strip()
    msg = bot.send_message(chat_id, "📞 Telefon raqamingizni kiriting:")
    bot.register_next_step_handler(msg, get_age, name, address, school)


def get_age(message, name, address, school):
    chat_id = message.chat.id
    phone = message.text.strip()
    msg = bot.send_message(chat_id, "🎂 Yoshingizni kiriting:")
    bot.register_next_step_handler(msg, check_age, name, address, school, phone)


def check_age(message, name, address, school, phone):
    chat_id = message.chat.id
    try:
        age = int(message.text.strip())
        if age < 5 or age > 16:
            bot.send_message(chat_id, "🚫 Kechirasiz, yoshingiz test uchun mos emas. Xayr!")
            return
    except ValueError:
        bot.send_message(chat_id, "❌ Iltimos, yoshingizni to'g'ri kiriting!")
        return

    user = {
        "id": chat_id, "name": name, "address": address, "school": school,
        "phone": phone, "age": age, "results": {}, "total_score": 0
    }
    users.append(user)
    save_data(USERS_FILE, users)

    bot.send_message(chat_id, "✅ Ma'lumotlaringiz saqlandi!")
    send_main_menu(chat_id)
def show_my_results(chat_id):
    """Foydalanuvchining test natijalarini ko‘rsatish."""
    user = next((u for u in users if u['id'] == chat_id), None)
    if not user:
        bot.send_message(chat_id, "Iltimos, avval /start buyrug'ini bering va ro'yxatdan o'ting!")
        return

    if not user.get("results"):
        bot.send_message(chat_id, "Siz hali testdan o'tmagansiz.")
        return

    score = user.get("total_score", 0)
    bot.send_message(chat_id, f"📊 Sizning test natijangiz: {score} ball")


def send_main_menu(chat_id):
    """Asosiy menyuni oddiy tugmalar shaklida chiqarish."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        KeyboardButton("📋 Testni boshlash"),
        KeyboardButton("📊 Mening natijam"),
        KeyboardButton("ℹ️ Men haqimda"),
        KeyboardButton("🏆 Reyting")
    )

    bot.send_message(chat_id, "👇 Quyidagilardan birini tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["📋 Testni boshlash", "📊 Mening natijam", "ℹ️ Men haqimda", "🏆 Reyting"])
def handle_main_menu(message):
    chat_id = message.chat.id
    text = message.text

    if text == "📋 Testni boshlash":
        start_test(chat_id)

    elif text == "📊 Mening natijam":
        show_my_results(chat_id)

    elif text == "ℹ️ Men haqimda":
        show_my_info(chat_id)

    elif text == "🏆 Reyting":
        show_ranking(chat_id)

def show_my_info(chat_id):
    """Foydalanuvchining shaxsiy ma'lumotlarini ko‘rsatish."""
    user = next((u for u in users if u['id'] == chat_id), None)
    if not user:
        bot.send_message(chat_id, "Iltimos, avval /start buyrug'ini bering va ro'yxatdan o'ting!")
        return

    info = (f"👤 *Ismingiz:* {user['name']}\n"
            f"🏠 *Manzilingiz:* {user['address']}\n"
            f"🏫 *Maktabingiz:* {user['school']}\n"
            f"📞 *Telefon:* {user['phone']}\n"
            f"🎂 *Yoshingiz:* {user['age']}")

    bot.send_message(chat_id, info, parse_mode="Markdown")





@bot.message_handler(commands=['test'])
def start_test(chat_id):
    """Testni boshlash va birinchi savolni chiqarish."""
    user = next((u for u in users if u['id'] == chat_id), None)
    if not user:
        bot.send_message(chat_id, "Iltimos, avval /start buyrug'ini bering va ro'yxatdan o'ting!")
        return
    user['results'] = {}
    user['in_test'] = True  # 🟢 Test boshlandi
    ask_question(chat_id, 0)

def ask_question(chat_id, index):
    """Test savollarini chiqarish (variantlar inline tugma sifatida chiqadi)."""
    user = next((u for u in users if u['id'] == chat_id), None)
    if not user:
        return

    if index >= len(test_savollari):
        user['in_test'] = False  # 🔴 Test tugadi
        calculate_results(chat_id)
        return

    question = test_savollari[index]

    # 🟢 Inline tugmalar yaratish
    markup = InlineKeyboardMarkup()
    for variant in question['variants']:
        markup.add(InlineKeyboardButton(variant['text'], callback_data=f"answer_{index}_{variant['kasb']}_{variant['ball']}"))

    bot.send_message(chat_id, question['savol'], reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def process_answer(call):
    """Foydalanuvchi javob tugmasini bosganda ishlov berish."""
    chat_id = call.message.chat.id
    _, index, kasb, ball = call.data.split("_")
    index, ball = int(index), int(ball)

    user = next((u for u in users if u['id'] == chat_id), None)
    if user:
        user['results'][kasb] = user['results'].get(kasb, 0) + ball
        save_data(USERS_FILE, users)

    try:
        bot.answer_callback_query(call.id, "Javob qabul qilindi ✅")
    except Exception as e:
        print(f"Callback query xatosi: {e}")

    ask_question(chat_id, index + 1)
def calculate_results(chat_id):
    """Test natijalarini hisoblash va natijalarni chiqarish."""
    user = next((u for u in users if u['id'] == chat_id), None)
    if not user:
        return

    user['in_test'] = False  # 🔴 Test yakunlandi
    results = user['results']

    # 🔹 Eski klaviaturani olib tashlaymiz (bo‘sh klaviatura yuborish orqali)
    bot.send_message(chat_id, "✅ Test yakunlandi. Natijalaringiz:", reply_markup=InlineKeyboardMarkup())

    if not results:
        bot.send_message(chat_id, "Siz hech qanday savolga javob bermadingiz.")
        send_main_menu(chat_id)  # 🔥 Test natijasidan keyin menyuga qaytish
        return

    top_kasb = max(results, key=results.get)
    total_points = sum(results.values())
    user['total_score'] = total_points
    save_data(USERS_FILE, users)

    bot.send_message(chat_id,
                     f"📋 Sizning kasbingiz: {top_kasb} ({results[top_kasb]} ball)\n🎯 Umumiy ball: {total_points}")

    show_ranking(chat_id)  # 🔥 Reyting ko‘rsatish
    send_main_menu(chat_id)  # 🔥 Test natijasidan keyin menyuga qaytish

    if is_in_top_10(user):
        send_certificate(chat_id, user)
def save_answer(message, index):
    chat_id = message.chat.id
    answer = message.text.strip()
    question = test_savollari[index]

    user = next((u for u in users if u['id'] == chat_id), None)
    if user:
        for variant in question['variants']:
            if answer.startswith(variant['text']):
                kasb = variant['kasb']
                ball = variant['ball']
                user['results'][kasb] = user['results'].get(kasb, 0) + ball
                save_data(USERS_FILE, users)
                break

    ask_question(chat_id, index + 1)



def show_ranking(chat_id):
    sorted_users = sorted(users, key=lambda u: u.get("total_score", 0), reverse=True)
    ranking_text = "🏆 Eng kuchli TOP  foydalanuvchilar:\n\n"

    for i, user in enumerate(sorted_users[:1000], start=1):
        ranking_text += f"{i}. {user['name']} - {user.get('total_score', 0)} ball\n"

    bot.send_message(chat_id, ranking_text)


def is_in_top_10(user):
    sorted_users = sorted(users, key=lambda u: u.get("total_score", 0), reverse=True)
    return user in sorted_users[:10]


@bot.message_handler(commands=['users'])
def show_users(message):
    chat_id = message.chat.id

    if not users:
        bot.send_message(chat_id, "📂 Foydalanuvchilar ro'yxati bo'sh.")
        return

    users_text = "📋 Ro'yxatdan o'tgan foydalanuvchilar:\n\n"
    for user in users:
        results_text = "\n".join([f"📚 {subject}: {score}" for subject, score in user['results'].items()])

        users_text += f"🆔 ID: {user['id']}\n👤 Ism: {user['name']}\n🏠 Manzil: {user['address']}\n" \
                      f"📞 Telefon: {user['phone']}\n🎂 Yosh: {user['age']}\n" \
                      f"🏫 Maktab: {user['school']}\n🎯 Natijalar:\n{results_text}\n" \
                      f"⭐ Jami ball: {user['total_score']}\n----------------------\n"


    bot.send_message(chat_id, users_text)


def send_certificate(chat_id, user):
    global image, top_score
    user_name = user['name']  # Foydalanuvchi ismini olish
    # Rasmni ochish
    if user["results"]:
        top_career = max(user["results"], key=user["results"].get)  # Eng yuqori ball olgan kasb
        top_score = user["results"][top_career]  # Eng yuqori ball
        print(f"Foydalanuvchi {user_name} eng yuqori ballni '{top_career}' kasbida oldi: {top_score}")
    else:
        top_career = "Noma'lum"
        print(f"Foydalanuvchi {user_name} natijalari mavjud emas!")


    if top_career == 'IT':
        image =  Image.open(certificate_pathit)
    elif top_career =='Biznes':
        image =  Image.open(certificate_pathbiznes)
    elif top_career =='Filologiya':
        image =  Image.open(certificate_pathtibbiyot)
    elif top_career == 'Robotatexnika':
        image = Image.open(certificate_pathitharbiy)

    draw = ImageDraw.Draw(image)
    ball = ImageDraw.Draw(image)
    # Shrift sozlamalari

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 35
    font = ImageFont.truetype(font_path, font_size)

    font_path1 = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size1 = 17
    font1 = ImageFont.truetype(font_path1, font_size1)

    # Ismni joylashtirish koordinatalari
    text_position = (400, 400)  # Matnni joylashtirish uchun mos keladigan joy
    text_color = (0, 0, 0)  # Qora rang
    text_position1 = (710, 548)  # Matnni joylashtirish uchun mos keladigan joy
    text_color1 = (0, 0, 0)
    # Ismni rasmga qo‘shish
    draw.text(text_position, user_name, font=font, fill=text_color)
    ball.text(text_position1, f"  {top_score}  ball", font=font1, fill=text_color1)

    # Rasmni saqlash
    output_path = f"certificate_{chat_id}.jpg"
    image.save(output_path)




    if os.path.exists(output_path):
        with open(output_path, "rb") as cert:
            bot.send_document(chat_id, cert, caption=f"🎉 Tabriklaymiz, {user['name']}! Siz TOP  talikka kirdingiz!")
    else:
        bot.send_message(chat_id, "❌ Sertifikat fayli topilmadi!")
    if os.path.exists(output_path):
        os.remove(output_path)

    def signal_handler(sig, frame):
        print("Bot to‘xtatildi.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)  # Ctrl + C
    signal.signal(signal.SIGTERM, signal_handler)  # kill buyruqlari

    def run_bot():
        while True:
            try:
                print("Bot ishga tushdi...")
                bot.polling(none_stop=True, timeout=60)
            except Exception as e:
                print(f"Xatolik yuz berdi: {e}")
                time.sleep(5)

    if __name__ == "__main__":
        run_bot()
bot.polling(none_stop=True)
