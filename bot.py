import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
import os
from aiogram import Bot, Dispatcher, types

# Включите логирование, чтобы видеть, что происходит
logging.basicConfig(level=logging.INFO)

# Токен вашего бота (теперь получаем из переменной окружения)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if BOT_TOKEN is None:
    print("Error: BOT_TOKEN environment variable not set!")
    exit()  # Exit the program if BOT_TOKEN is not set

# ID администратора (теперь получаем из переменной окружения)
try:
    ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID"))
except (ValueError, TypeError):
    print("Error: ADMIN_CHAT_ID environment variable not set or not an integer!")
    ADMIN_CHAT_ID = None  # Or some default value if appropriate
    exit() # Exit the program if ADMIN_CHAT_ID is not valid

# Путь к картинке
IMAGE_PATH = "image1.jpg"  # Замените на фактический путь к вашей картинке

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# FSM (Состояния)
class DemoForm(StatesGroup):
    waiting_for_something = State()  # Состояние для ожидания чего-либо

# --- Хэндлеры ---
# Шаг 1: Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    try:
        # Отправляем картинку
        with open(IMAGE_PATH, "rb") as photo:
            await bot.send_photo(message.chat.id, photo=types.BufferedInputFile(photo.read(), filename="image1.jpg"))

        # Отправляем текст с кнопкой
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить демку", callback_data="send_demo")]
        ])
        await message.answer(
            "Йо!\n"
            "Это бот музыкального лейбла «RS Records» и команды Рашн Стаил. Если ты артист, пишешь музыку и хочешь быть услышанным — тебе к нам",
            reply_markup=keyboard
        )

    except FileNotFoundError:
        await message.answer("Ошибка: Файл изображения не найден. Убедитесь, что файл 'image.jpg' находится в правильном месте.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await message.answer("Произошла ошибка при отправке сообщения. Попробуйте позже.")

# Шаг 2: Обработчик нажатия кнопки "Хочу отправить демку"
@dp.callback_query(F.data == "send_demo")
async def send_demo_callback(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить анкету", callback_data="fill_form")]
    ])
    await bot.send_message(callback.message.chat.id,
        "Поделись с нами треком, если:\n"
        "1. Трек подходит жанрово нашему лейблу\n"
        "2. Трек закончен на 90% <i>(не обязательно, чтобы трек был отмастерен и сведён)</i>\n"
        "3. Если у тебя много демок, выбери 1-2 лучших для отправки. Не отправляй сразу всё\n"
        "4. К предложению принимаются <b><ins>ТОЛЬКО</b></ins> не подписанные другими лейблами демо-треки",
        reply_markup=keyboard
    )
    await callback.answer()

# Шаг 3: Обработчик нажатия кнопки "Заполнить анкету"
@dp.callback_query(F.data == "fill_form")
async def fill_form_callback(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id,
        "Отправляй всё <b><ins>ОДНИМ сообщением</b></ins>\n\nРасскажи нам о себе:\n"
        "1. Артистический псевдоним\n"
        "2. Кратко о себе <i>(как зовут, откуда ты, как давно занимаешься музыкой, на каких лейблах выпускаешь музыку, играешь ли ты на других вечеринках (если да, то на каких)</i>)\n"
        "3. Прикрепи ссылку на свой Instagram\n"
        "4. Название трека\n"
        "5. Жанр трека\n"
        "6. Ссылка на твою карточку артиста в Яндекс музыке\n"
        "7. Твой ник в Telegram\n"
        "8. Прикрепи к сообщению демку в формате MP3"
    )
    await state.set_state(DemoForm.waiting_for_something) # Ждем чего угодно
    await callback.answer()

# Шаг 4 & 5: Обрабатываем любое сообщение и пересылаем
@dp.message(DemoForm.waiting_for_something)
async def process_anything(message: Message, state: FSMContext):
    try:
        await bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=message.chat.id, message_id=message.message_id)  # Пересылаем сообщение в чат админа
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")
        await message.reply("Произошла ошибка при пересылке сообщения.")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить ещё одну демку", callback_data="send_demo")]
    ])
    await bot.send_message(message.chat.id,
        "Супер!\nАнкета отправлена \n\nПослушаем и дадим обратную связь",
        reply_markup=keyboard
    )
    await state.clear()  # Сбрасываем состояние

# Шаг 6: Обработка кнопки "Отправить еще одну демку"
@dp.callback_query(F.data == "send_demo")
async def send_demo_callback(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить анкету", callback_data="fill_form")]
    ])
    await bot.send_message(callback.message.chat.id,
        "Поделись с нами треком, если:\n"
        "1. Трек подходит жанрово нашему лейблу\n"
        "2. Трек закончен на 90% <i>(не обязательно, чтобы трек был отмастерен и сведён)</i>\n"
        "3. Если у тебя много демок, выбери 1-2 лучших для отправки. Не отправляй сразу всё\n"
        "4. К предложению принимаются ТОЛЬКО не подписанные другими лейблами демо-треки",
        reply_markup=keyboard
    )
    await callback.answer()

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
