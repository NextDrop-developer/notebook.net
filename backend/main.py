import os
import json
import smtplib
import asyncio
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ContentType
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL = os.getenv("EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== EMAIL FUNCTION =====
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL, EMAIL_PASS)
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("EMAIL ERROR:", e)

async def send_async(*args):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_email, *args)

# ===== HANDLER =====
@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        version = data.get("version")

        order_id = random.randint(10000, 99999)

        # ---- CLIENT EMAIL ----
        client_body = f"""
        <h2>Спасибо, {name}!</h2>
        <p>Ваш предзаказ принят 🤍</p>
        <p><b>Номер заказа:</b> #{order_id}</p>
        <p>Мы скоро свяжемся с вами.</p>
        """

        # ---- MANAGER EMAIL ----
        manager_body = f"""
        <h2>🛒 Новый заказ</h2>

        <p><b>ID:</b> #{order_id}</p>
        <p><b>Имя:</b> {name}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Телефон:</b> {phone}</p>
        <p><b>Продукт:</b> {version}</p>

        <hr>

        <p><b>Telegram ID:</b> {message.from_user.id}</p>
        <p><b>Username:</b> @{message.from_user.username}</p>

        <p><b>Дата:</b> {message.date}</p>
        """

        await send_async(email, "Подтверждение заказа", client_body)
        await send_async(MANAGER_EMAIL, "Новый заказ", manager_body)

        await message.answer(f"Спасибо, {name}! Заказ #{order_id} оформлен.")

    except Exception as e:
        print("ERROR:", e)
        await message.answer("Ошибка при обработке заказа.")

# ===== START =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
