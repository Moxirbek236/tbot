import logging
import random
import asyncio
import datetime
import pytz
import json
import os
import html
import schedule
import requests
import nest_asyncio
from keep_alive import keep_alive
from geopy.geocoders import Nominatim
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
from weather import get_weather, get_image_url_by_weather, vaqt_turini_aniqlash, tarjima_qil
# from utils import vaqt_turini_aniqlash
from settings import TOKEN, CHAT_ID
from messages import kun_salomlari, kech_salomlari
from utils import log_yoz, save_user

BOT_TOKEN = "7818484616:AAG6UZLNbKi4Cm5SDJloF-FOhOtmIBeRWtM"

bot = Bot(token=TOKEN)

geolocator = Nominatim(user_agent="weather-bot")

TONG_RASM_PATH = "images/tong.jpg"
JUMA_RASM_PATH = "images/juma.jpg"
TUNGI_RASM_PATH = "images/tun.jpg"


# === SALOMLAR ===
async def tongi_salom():
  weather = get_weather()
  now = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
  hafta_kuni = now.strftime("%A")  # Monday, Tuesday, ...

  salom_matn = kun_salomlari.get(hafta_kuni, "🌞 Hayrli tong!")
  matn = f"{salom_matn}\n\n{weather['text']}"

  # Rasmlar yo'lini tanlash
  if hafta_kuni == "Friday":
      image_path = JUMA_RASM_PATH
  else:
      image_path = TONG_RASM_PATH

  # ✅ Fayl mavjudligini tekshirish
  if not os.path.exists(image_path):
      print(f"❌ Fayl topilmadi: {image_path}")
      return  # stop execution if image is missing

  # Rasmni ochish va yuborish - caption da salom va ob-havo
  with open(image_path, "rb") as photo:
      await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=matn)


async def faqat_obhavo():
  weather = get_weather()
  now = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
  weekday = now.strftime("%A")

  img_path = JUMA_RASM_PATH if weekday == "Friday" else TONG_RASM_PATH

  with open(img_path, "rb") as photo:
      await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=weather['text'])

  log_yoz("🌤 Ob-havo yuborildi.")


async def kechki_salom():
  now = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
  day = now.strftime('%A')  # Monday, Tuesday, ...
  salom_matn = kech_salomlari.get(day, "🌙 Hayrli tun!")  # agar topilmasa default

  weather = get_weather()
  matn = f"{salom_matn}\n\n{weather['text']}"

  # Fayl mavjudligini va hajmini tekshirish
  image_path = "images/tun.jpeg"
  if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
      image_path = "images/tong.jpg"  # fallback

  with open(image_path, "rb") as photo:
      await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=matn)

  log_yoz("🌙 Kechki salom yuborildi.")



def jadval_tongi_salom():
  asyncio.create_task(tongi_salom())
  log_yoz("⏰ Tongi salom jadval asosida yuborildi.")


def jadval_faqat_obhavo():
  asyncio.create_task(faqat_obhavo())
  log_yoz("⏰ Ob-havo jadval asosida yuborildi.")


def jadval_kechki_salom():
  asyncio.create_task(kechki_salom())
  log_yoz("⏰ Kechki salom jadval asosida yuborildi.")


last_sent_minute = None  # global o'zgaruvchi


async def schedule_loop():
  global last_sent_minute
  while True:
    now = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
    current_minute = now.strftime("%Y-%m-%d %H:%M")

    if last_sent_minute != current_minute:
      if now.strftime("%H:%M") == "06:20":
        await tongi_salom()
        log_yoz("⏰ Tongi salom yuborildi.")
      elif now.strftime("%H:%M") == "22:20":
        await kechki_salom()
        log_yoz("⏰ Kechki salom yuborildi.")
      elif now.minute % 30 == 0:
        await faqat_obhavo()
        log_yoz("⏰ Faqat ob-havo yuborildi.")

      last_sent_minute = current_minute

    await asyncio.sleep(
        5)  # 5 soniyada tekshir, ammo 1 daqiqa ichida faqat 1 marta yuboradi


# schedule.every().day.at("18:25").do(jadval_tongi_salom)  # tonggi salom
# schedule.every().day.at("18:26").do(jadval_faqat_obhavo)  # tushgi ob-havo
# schedule.every().day.at("18:27").do(jadval_faqat_obhavo)  # kechki ob-havo
# schedule.every().day.at("18:28").do(jadval_kechki_salom)  # kechki salom

# async def schedule_loop():
#   while True:
#     schedule.run_pending()
#     await asyncio.sleep(1)

# === HANDLERS ===

# from geopy.geocoders import Nominatim


async def handle_location(update: Update, context: CallbackContext):
  user = update.effective_user
  if user:
    save_user(user.id, user.first_name, user.username)
  location = update.message.location
  lat, lon = location.latitude, location.longitude

  # Reverse geocoding
  geolocator = Nominatim(user_agent="my-telegram-bot")
  try:
    location_info = geolocator.reverse((lat, lon), language='uz')
    manzil = location_info.address if location_info else "Manzil aniqlanmadi"
  except:
    manzil = "Manzilni aniqlab bo‘lmadi"

  # Ob-havoni olish
  weather = get_weather(lat, lon)
  text = (f"📍 Siz yuborgan joy: {manzil}\n"
          f"{weather['text']}")

  await update.message.reply_text(text)

  print(f"📍 Lokatsiya: {user.full_name} ({user.username}) | {lat}, {lon}")
  print(f"📍 Manzil: {manzil}")

  save_user(user.id, user.first_name, user.username)


async def handle_text(update: Update, context: CallbackContext):
  user = update.effective_user
  if user:
    save_user(user.id, user.first_name, user.username)
  # user = update.effective_user
  text = update.message.text
  # save_user(user)
  log_yoz(f"✉️ {user.first_name} (@{user.username}): {text}")
  # await update.message.reply_text("Xabaringiz qabul qilindi. Rahmat!")


# async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   user = update.effective_user
#   chat = update.effective_chat

#   text = f"✅ Start buyrug‘i: {html.escape(user.full_name)} (@{user.username}) | Chat ID: {chat.id}"
#   await update.message.reply_text(text, parse_mode="HTML")
#   # f"✅ Start buyrug‘i: {user.full_name} (@{user.username}) | Chat ID: {chat.id}"
#   print(f"✉️ {user.first_name} (@{user.username}): {text}")

# async def jadval_loop():
#   while True:
#     now = datetime.datetime.now(
#         pytz.timezone("Asia/Tashkent")).strftime("%H:%M")

#     if now == "18:28":
#       await tongi_salom()
#       log_yoz("⏰ Tongi salom yuborildi.")

#     elif now == "18:29":
#       await kechki_salom()
#       log_yoz("⏰ Kechki salom yuborildi.")

#     elif now[-2:] in ["00", "30"]:  # Har 30 daqiqa
#       await faqat_obhavo()
#       log_yoz("⏰ Faqat ob-havo yuborildi.")

#     await asyncio.sleep(60)


# --- Boshi ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user

  # Terminalga yozamiz
  print(
      f"✅ Start buyrug‘i: {user.full_name} (@{user.username}) | Chat ID: {update.effective_chat.id}"
  )

  # Xabar yuboramiz
  await update.message.reply_text(
      "👋 Salom! Ob-havo haqida ma’lumot olish uchun lokatsiya yuboring.")

  # Foydalanuvchini faylga saqlaymiz
  user_data = {
      "id": user.id,
      "first_name": user.first_name,
      "username": user.username,
      "chat_id": update.effective_chat.id
  }

  # Faylga yozish
  if os.path.exists("users.json"):
    with open("users.json", "r", encoding="utf-8") as f:
      users = json.load(f)
  else:
    users = []

  if not any(u["id"] == user.id for u in users):
    users.append(user_data)
    with open("users.json", "w", encoding="utf-8") as f:
      json.dump(users, f, ensure_ascii=False, indent=2)
    print("🆕 Yangi foydalanuvchi qo‘shildi.")


async def help_command(update: Update, context: CallbackContext):
  await update.message.reply_text(
      "Botdan foydalanish uchun lokatsiya yuboring yoki /start ni bosing.")


# === START ===

if __name__ == '__main__':
  from keep_alive import keep_alive
  keep_alive()  # Flask server ishga tushadi

  from utils import log_yoz
  log_yoz("🚀 Bot ishga tushmoqda...")

  import nest_asyncio
  nest_asyncio.apply()  # Replitda asyncio konfliktini oldini oladi

  async def start():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    asyncio.create_task(schedule_loop())  # Jadvalni ishga tushuramiz
    # asyncio.create_task(schedule_loop())

    # application = ApplicationBuilder().token(BOT_TOKEN).build()
    # application.add_handler(CommandHandler("start", about_bot))
    # application.add_handler(
    #     MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    # application.run_polling()

    # asyncio.create_task(jadval_loop())

    await application.run_polling()

  # Replitda ishlaydigan holatda
  asyncio.get_event_loop().create_task(start())

  # Bot ishlashdan to‘xtamasligi uchun doimiy asyncio loopni saqlab turamiz
  asyncio.get_event_loop().run_forever()

asyncio.get_event_loop().run_until_complete(start())