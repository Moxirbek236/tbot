import requests
import pytz
from datetime import datetime
import requests

# OpenWeatherMap API kalitingizni bu yerga yozing (asosiy fayldan import qilish ham mumkin)
OWM_API_KEY = "57e2dc54a5dfd435e2bb7586af756faf"

def tarjima_qil(matn: str) -> str:
    """Ob-havo tavsifini ingliz tilidan o'zbek tiliga tarjima qiladi."""
    tarjimalar = {
        "clear sky": "ochiq osmon",
        "few clouds": "biroz bulutli",
        "scattered clouds": "sochilgan bulutlar",
        "broken clouds": "yoriq bulutlar",
        "shower rain": "kuchli yomg'ir",
        "rain": "yomg'ir",
        "light rain": "yengil yomg'ir",
        "thunderstorm": "momaqaldiroq",
        "snow": "qor",
        "mist": "tuman",
        "overcast clouds": "qalin bulutlar",
        "haze": "tutun",
        "fog": "tuman",
    }
    return tarjimalar.get(matn.lower(), matn)

def get_weather(lat=41.3111, lon=69.2797) -> dict:
    """Berilgan koordinatalar bo'yicha ob-havo ma'lumotini qaytaradi (Toshkent default)."""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang=en"
    r = requests.get(url)
    data = r.json()

    if "weather" not in data or "main" not in data:
        return {"text": "❗ Ob-havo ma'lumotlarini olishda xatolik.", "icon": "01d"}

    temp = data['main']['temp']
    desc = data['weather'][0]['description']
    icon = data['weather'][0]['icon']
    location_name = data.get('name', 'Noma\'lum joy')

    desc_uz = tarjima_qil(desc)

    # Har doim manzil, harorat va holatni ko'rsatish
    text = f"📍 Manzil: {location_name}\n🌡 Harorat: {round(temp)}°C\n🌥 Holat: {desc_uz.capitalize()}"

    return {"text": text, "icon": icon}

def get_image_url_by_weather(icon_code: str, vaqt: str = "kun") -> str:
    """Ob-havo ikonasi va vaqtga qarab rasm URLni qaytaradi."""
    asosiy = icon_code[:2]  # Masalan: '01', '02'
    base = "https://raw.githubusercontent.com/moxirbek/weather-images/main"

    mapping = {
        "01": f"{base}/{vaqt}/sun.jpg",
        "02": f"{base}/{vaqt}/cloudy.jpg",
        "03": f"{base}/{vaqt}/clouds.jpg",
        "04": f"{base}/{vaqt}/dark_clouds.jpg",
        "09": f"{base}/{vaqt}/rain.jpg",
        "10": f"{base}/{vaqt}/light_rain.jpg",
        "11": f"{base}/{vaqt}/storm.jpg",
        "13": f"{base}/{vaqt}/snow.jpg",
        "50": f"{base}/{vaqt}/fog.jpg",
    }

    return mapping.get(asosiy, f"{base}/{vaqt}/default.jpg")

def vaqt_turini_aniqlash():
    """Toshkent vaqti bo‘yicha kun vaqtini aniqlaydi: tong, kun, kech."""
    hozir = datetime.now(pytz.timezone("Asia/Tashkent"))
    soat = hozir.hour

    if 5 <= soat < 12:
        return "tong"
    elif 12 <= soat < 18:
        return "kun"
    else:
        return "tun"



def get_weather_by_location(lat=None, lon=None):
    if lat is None or lon is None:
        # Toshkentning default koordinatasi (agar lokatsiya bo'lmasa)
        lat, lon = 41.3111, 69.2797

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang=en"
    response = requests.get(url)
    data = response.json()

    # Tarjima qilish
    description_uz = tarjima_qil(data['weather'][0]['description'])

    return {
        "temp": data["main"]["temp"],
        "description": description_uz,
        "icon": data["weather"][0]["icon"],
        "text": f"📍 Manzil: {data['name']}\n🌡 Harorat: {round(data['main']['temp'])}°C\n🌤 Holat: {description_uz.capitalize()}"
    }