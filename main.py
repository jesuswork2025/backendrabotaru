from fastapi import FastAPI
from pydantic import BaseModel
import telegram
from telegram.error import TelegramError

# Плейсхолдеры для токена Telegram-бота и Chat ID
TELEGRAM_BOT_TOKEN = "8192966834:AAFy9AyJH3iJQa2xMh5XJL5EJetTtqZuBFQ"
TELEGRAM_CHAT_ID = "7776021432"

app = FastAPI()

class UserData(BaseModel):
    name: str
    surname: str
    age: str
    city: str
    experience: str
    phone_number: str
    communication_type: str

async def send_telegram_message(data: dict):
    message = f"""Новая заявка:
Имя: {data.get('name')}
Фамилия: {data.get('surname')}
Возраст: {data.get('age')}
Город: {data.get('city')}
Стаж употребления: {data.get('experience')}
Номер телефона: {data.get('phone_number')}
Тип связи: {data.get('communication_type')}
"""
    try:
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            print("Ошибка: TELEGRAM_BOT_TOKEN не задан или является плейсхолдером.")
            return
        if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID_HERE":
            print("Ошибка: TELEGRAM_CHAT_ID не задан или является плейсхолдером.")
            return

        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Сообщение успешно отправлено в Telegram.")
    except TelegramError as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при отправке сообщения в Telegram: {e}")


@app.post("/submit_data")
async def submit_data(data: UserData):
    await send_telegram_message(data.model_dump())
    return data