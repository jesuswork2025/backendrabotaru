from fastapi import FastAPI
from pydantic import BaseModel
import telegram
from telegram.error import TelegramError
import time
import threading
import requests
import uvicorn # Добавлен для локального запуска и тестирования keep-alive
# from fastapi import BackgroundTasks # BackgroundTasks не используется в текущей реализации keep-alive
from contextlib import asynccontextmanager

# URL сервера для keep-alive запроса.
# Для локального запуска это http://127.0.0.1:8000 или http://localhost:8000
# Для развернутого приложения это будет его публичный URL.
SERVER_URL = "https://backendrabotaru.onrender.com" # Убедитесь, что URL и порт соответствуют запуску uvicorn

def keep_alive_ping():
    """
    Отправляет GET-запрос на эндпоинт /ping для поддержания активности.
    """
    while True:
        try:
            # Убедитесь, что SERVER_URL правильно настроен для вашего окружения
            response = requests.get(f"{SERVER_URL}/ping")
            if response.status_code == 200:
                print(f"Keep-alive ping successful: {response.json()}")
            else:
                print(f"Keep-alive ping failed with status: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Keep-alive ping request failed: {e}")
        time.sleep(180) # 3 минуты

@asynccontextmanager
async def lifespan(app_instance: FastAPI): # Переименовал app в app_instance чтобы не конфликтовать с глобальным app
    # Запуск фоновой задачи при старте приложения
    thread = threading.Thread(target=keep_alive_ping, daemon=True)
    thread.start()
    print("Keep-alive ping thread started.")
    yield
    # Код для очистки при остановке приложения (если необходимо)
    print("Keep-alive ping thread stopping (application shutdown).")

# Плейсхолдеры для токена Telegram-бота и Chat ID
TELEGRAM_BOT_TOKEN = "8192966834:AAFy9AyJH3iJQa2xMh5XJL5EJetTtqZuBFQ"
TELEGRAM_CHAT_ID = "7776021432"

app = FastAPI(lifespan=lifespan)

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

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}
@app.get("/ping")
async def ping():
    """
    Простой эндпоинт для проверки доступности сервера.
    """
    return {"status": "ok", "message": "Server is alive!"}

# Для локального запуска (если этот файл запускается напрямую)
if __name__ == "__main__":
    # Важно: для keep-alive запросов, которые идут на сам сервер,
    # uvicorn должен быть запущен с host="0.0.0.0" или аналогичным,
    # чтобы быть доступным по сети, а не только с localhost.
    # Если вы запускаете через `uvicorn main:app --reload`, эта часть не выполняется.
    # Этот блок добавлен для удобства тестирования.
    print(f"Starting server. Keep-alive pings will target {SERVER_URL}/ping")
    uvicorn.run(app, host="0.0.0.0", port=8000)