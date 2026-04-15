import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ContentType

# === НАСТРОЙКИ (ЗАПОЛНИ СВОЁ) ===
TOKEN = "7761399853:AAG01cSKwZODu3KlYL4RTnZgD0ck-wGP4gI"
SENDER_EMAIL = "notebook.net.info@gmail.com" 
SENDER_PASSWORD = "opadmpftxiczadle" 
# ===============================

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

def send_confirmation_email(user_email, user_name, version_name):
    msg = MIMEMultipart()
    msg['From'] = f"Дай себе год <{SENDER_EMAIL}>"
    msg['To'] = user_email
    msg['Subject'] = "Ваш предзаказ принят 🤍"

    body = f"""
    <html>
    <body style="font-family: sans-serif;">
        <h2 style="color: #2F4F4F;">Привет, {user_name}!</h2>
        <p>Спасибо за предзаказ блокнота <b>«Дай себе год»</b>.</p>
        <p>Мы получили твою заявку на издание: <b>{version_name}</b>.</p>
        <p>Скоро мы свяжемся с тобой для уточнения деталей оплаты и доставки.</p>
        <br>
        <p><i>С любовью, команда проекта.</i></p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        logging.error(f"Ошибка почты: {e}")
        return False

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Открой приложение для предзаказа.")

@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def get_data(message: types.Message):
    try:
        # Получаем данные из Mini App
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)
        
        name = data.get('name')
        email = data.get('email')
        version = data.get('version')

        # Отправляем письмо
        email_status = send_confirmation_email(email, name, version)
        
        res_text = f"✨ Спасибо, {name}!\n\nЗаказ на {version} принят."
        if email_status:
            res_text += f"\nПодтверждение отправлено на {email}."
        
        await message.answer(res_text)
        
    except Exception as e:
        await message.answer("Произошла ошибка при обработке заказа.")
        logging.error(f"Ошибка Web App Data: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
