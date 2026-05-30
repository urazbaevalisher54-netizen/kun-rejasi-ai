import os
import telebot
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler

# ⚠️ DIQQAT: Bot tokeningiz va Gemini kalitingizni mana shu yerga qo'ying!
BOT_TOKEN = "8933792186:AAHSccAm1LTFX16eE8UZLS3cfwIS4CAeuc8"
GEMINI_KEY = "AQ.Ab8RN6ISjwSvOAQ8sXfhyCSsXt8EJWzXnljv8E0mKvGFHQ6b9g"
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

scheduler = BackgroundScheduler()
scheduler.start()

user_history = {}

SYSTEM_INSTRUCTION = """
Siz foydalanuvchining shaxsiy aqlli yordamchisiz. Ismingiz: Kun Rejasi AI.
Vazifalaringiz:
1. Kunlik rejalarni soatbay tartibga solish va optimallash.
2. Savollarga aniq javob berish.
3. Doimo faqat o'zbek tilida muloqot qilish.
4. Oldingi suhbat kontekstini eslab qolish.
"""

def get_ai_response(user_id, text):
    if user_id not in user_history:
        user_history[user_id] = []
    
    messages = [{"role": "user", "parts": [SYSTEM_INSTRUCTION]}]
    for msg in user_history[user_id][-6:]:
        messages.append(msg)
    
    messages.append({"role": "user", "parts": [text]})
    
    try:
        response = model.generate_content(messages)
        user_history[user_id].append({"role": "user", "parts": [text]})
        user_history[user_id].append({"role": "model", "parts": [response.text]})
        return response.text
    except Exception:
        return "Kechirasiz, hozir bog'lanishda xatolik bo'ldi. Qayta urinib ko'ring."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Assalomu alaykum! Men sizning aqlli AI yordamchingizman. 🤖\n\n"
        "✅ Matnli va ovozli xabarlarni tushunaman\n"
        "✅ Kunlik reja tuzaman va savollarga javob beraman\n"
        "MAHSUS BUYRUK:\n"
        "⏰ Eslatma o'rnatish uchun: /eslatma 15:30 Vazifa ko'rinishida yozing."
    )
    bot.reply_to(message, welcome_text)

def send_reminder(chat_id, text):
    bot.send_message(chat_id, f"🔔 **ESLATMA:**\n\n{text}")

@bot.message_handler(commands=['eslatma'])
def set_reminder(message):
    try:
        parts = message.text.split(" ", 2)
        vaqt = parts[1]
        matn = parts[2]
        soat, minut = map(int, vaqt.split(":"))
        scheduler.add_job(send_reminder, 'cron', hour=soat, minute=minut, args=[message.chat.id, matn])
        bot.reply_to(message, f"✅ Eslatma muvaffaqiyatli o'rnatildi: soat {vaqt}da sizga xabar yuboraman.")
    except Exception:
        bot.reply_to(message, "⚠️ Format xato. Misol: `/eslatma 15:30 Dars qilish` ko'rinishida yozing.")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "🎙 Ovozli xabaringiz qabul qilindi. Telegram mobil versiyada ovozni matnga aylantirish kutubxonasini serveringizga bog'lamoqdamiz. Hozircha matn ko'rinishida yozib tursangiz, AI to'liq ishlaydi!")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    
    if "bugun nima qilishim kerak" in text.lower() or "vazifalar" in text.lower():
        ai_reply = get_ai_response(user_id, f"Foydalanuvchi bugungi vazifalarini so'rayapti. Unga rejalarini eslatib qo'ying: {text}")
    else:
        ai_reply = get_ai_response(user_id, text)
        
    bot.reply_to(message, ai_reply)

if __name__ == "__main__":
    bot.infinity_polling()
