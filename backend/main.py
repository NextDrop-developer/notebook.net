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

# Daten aus deiner .env (siehe dein Screenshot)
BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL_SENDER = os.getenv("EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_SENDER, EMAIL_PASS)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Fehler beim Mail-Versand: {e}")
        return False

@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: types.Message):
    try:
        # 1. Daten aus Web App auslesen
        data = json.loads(message.web_app_data.data)
        name = data.get("name")
        user_email = data.get("email")
        phone = data.get("phone")
        version = data.get("version")
        order_id = random.randint(1000, 9999)
        
        tg_username = f"@{message.from_user.username}" if message.from_user.username else "Kein Username"

        # 2. Sofortige Antwort an den Kunden im Telegram Chat
        reply_text = (
            f"✅ <b>Спасибо за предзаказ, {name}!</b>\n\n"
            f"Номер заказа: #{order_id}\n"
            f"Ваш Email: {user_email}\n"
            f"Ваш TG: {tg_username}\n\n"
            f"Менеджер скоро свяжется с вами! 💛"
        )
        await message.answer(reply_text, parse_mode="HTML")

        # 3. E-Mail an den KUNDEN (Bestätigung)
        client_mail_body = f"""
        <html>
            <body>
                <h2>Привет, {name}!</h2>
                <p>Спасибо за ваш предзаказ блокнота <b>"Дай себе год"</b>.</p>
                <p>Ваш номер заказа: <b>#{order_id}</b></p>
                <p>Менеджер напишет вам в ближайшее время для уточнения деталей оплаты и доставки.</p>
                <br>
                <p>С уважением,<br>Команда "Дай себе год"</p>
            </body>
        </html>
        """
        
        # 4. E-Mail an den MANAGER (Dich)
        manager_mail_body = f"""
        <h2>🛒 Новый заказ #{order_id}</h2>
        <p><b>Имя:</b> {name}</p>
        <p><b>Email:</b> {user_email}</p>
        <p><b>Телефон:</b> {phone}</p>
        <p><b>Версия:</b> {version}</p>
        <p><b>Telegram:</b> {tg_username} (ID: {message.from_user.id})</p>
        """

        # Mails im Hintergrund verschicken
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_email, user_email, f"Предзаказ #{order_id}", client_mail_body)
        await loop.run_in_executor(None, send_email, MANAGER_EMAIL, f"NEUER AUFTRAG #{order_id}", manager_mail_body)

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")

async def main():
    print("Bot läuft...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
