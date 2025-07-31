from datetime import datetime
import pytz
import json
import os

def log_yoz(matn: str):
    """Log yozuvlarini log.txt fayliga yozadi."""
    try:
        sana = datetime.now(pytz.timezone("Asia/Tashkent")).strftime("%Y-%m-%d %H:%M:%S")
        with open("log.txt", "a", encoding="utf-8") as fayl:
            fayl.write(f"[{sana}] {matn}\n")
    except Exception as e:
        print(f"Log yozishda xatolik: {e}")


def save_user(user_id, first_name, username):
    user_data = {
        "id": user_id,
        "first_name": first_name,
        "username": username
    }
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []
    if not any(u["id"] == user_id for u in users):
        users.append(user_data)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        print(f"✅ Yangi foydalanuvchi saqlandi: {first_name} (@{username})")

