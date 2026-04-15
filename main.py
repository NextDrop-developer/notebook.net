import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# --- КОНФИГ ---
TOKEN = '7761399853:AAG01cSKwZODu3KlYL4RTnZgD0ck-wGP4gI'
# Ссылка на твой сайт на GitHub Pages
WEB_APP_URL = 'https://compatible-pseudoenthusiastic-sarah.ngrok-free.dev/'
# Твой ID, чтобы бот присылал ТЕБЕ уведомления о заказах (узнай у @userinfobot)
ADMIN_ID = 6127906696

bot = Bot(token=TOKEN)
dp = Dispatcher()


# 1. Обработка команды /start
@dp.message(CommandStart())
async def start(message: types.Message):
    # Создаем кнопку для открытия Mini App
    kb = [
        [KeyboardButton(text="🎁 Оформить предзаказ", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(
        f"Привет, {message.from_user.first_name}! ✨\n\n"
        "Добро пожаловать в предзаказ блокнота «Дай себе год».\n"
        "Нажми на кнопку ниже, чтобы выбрать свою версию.",
        reply_markup=keyboard
    )


# 2. Ловим данные из Mini App (когда нажали "Подтвердить предзаказ")
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    # Данные приходят в виде строки JSON
    raw_data = message.web_app_data.data
    data = json.loads(raw_data)  # Превращаем в словарь Python

    # Формируем красивое сообщение для админа (тебя или Кати)
    order_text = (
        f"🚀 **НОВЫЙ ПРЕДЗАКАЗ!**\n"
        f"--------------------------\n"
        f"📔 Версия: {data['version']}\n"
        f"💰 Цена: {data['price']} €\n"
        f"--------------------------\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"📧 Email: {data['email']}\n"
        f"--------------------------\n"
        f"Юзернейм: @{message.from_user.username}"
    )

    # Отправляем подтверждение пользователю
    await message.answer(
        "✅ Спасибо! Твой предзаказ принят.\n"
        "Мы свяжемся с тобой перед отправкой первой партии."
    )

    # Отправляем данные тебе (админу)
    await bot.send_message(ADMIN_ID, order_text)


# Запуск бота
async def main():
    print("Бот запущен и готов к работе...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")