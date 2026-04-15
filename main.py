import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ContentType

# === НАСТРОЙКИ ПОЧТЫ (ВСТАВЬ СВОЁ) ===
SENDER_EMAIL = "notebook.net.info@gmail.com"  # Твоя новая почта
SENDER_PASSWORD = "opad mpft xicz adle"  # Тот желтый код из 16 букв (без пробелов)
# =====================================

TOKEN = "7761399853:AAG01cSKwZODu3KlYL4RTnZgD0ck-wGP4gI" # Вставь токен от BotFather, если его тут нет

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Функция для отправки письма
def send_confirmation_email(user_email, user_name, version_name):
    msg = MIMEMultipart()
    msg['From'] = f"Дай себе год <{SENDER_EMAIL}>"
    msg['To'] = user_email
    msg['Subject'] = "Ваш предзаказ принят 🤍"

    body = f"""
    <html>
    <body>
        <h2 style="color: #2F4F4F;">Привет, {user_name}!</h2>
        <p>Спасибо за интерес к проекту <b>«Дай себе год»</b>.</p>
        <p>Мы получили твой предзаказ на издание: <b>{version_name}</b>.</p>
        <p>В ближайшее время мы свяжемся с тобой для уточнения деталей оплаты и доставки.</p>
        <br>
        <hr>
        <p style="font-size: 12px; color: grey;">Это автоматическое письмо, на него не нужно отвечать.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        # Убираем пробелы из пароля на всякий случай
        clean_password = SENDER_PASSWORD.replace(" ", "")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, clean_password)
        server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка почты: {e}")
        return False

# Команда /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Нажми на кнопку ниже, чтобы оформить предзаказ.")

# Прием данных из Mini App
@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def get_webapp_data(message: types.Message):
    # Распаковываем данные из JSON
    data = json.loads(message.web_app_data.data)
    name = data.get('name')
    email = data.get('email')
    version = data.get('version')

    # 1. Пытаемся отправить письмо
    email_sent = send_confirmation_email(email, name, version)

    # 2. Отвечаем в Телеграм
    if email_sent:
        await message.answer(f"Спасибо, {name}! Заказ на {version} принят. Проверь почту {email} — письмо уже там! 📩")
    else:
        await message.answer(f"Спасибо, {name}! Заказ принят, но не удалось отправить письмо. Мы свяжемся с тобой позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
