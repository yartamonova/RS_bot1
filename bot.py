import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

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
IMAGE_PATH = "image3.jpg"  # Замените на фактический путь к вашей картинке

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML) # parse_mode передается напрямую
dp = Dispatcher()

# FSM (Состояния)
class DemoForm(StatesGroup):
    waiting_for_profile_info = State()  # Состояние для ожидания информации профиля (пункты 1-7)
    waiting_for_demo = State() # Состояние для ожидания демки (пункт 8)

# --- Хэндлеры ---
# Шаг 1: Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    try:
        # Отправляем картинку
        with open(IMAGE_PATH, "rb") as photo:
            await bot.send_photo(message.chat.id, photo=types.BufferedInputFile(photo.read(), filename="image3.jpg"))

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
        "4. К предложению принимаются <b><ins>ТОЛЬКО</ins></b> не подписанные другими лейблами демо-треки",
        reply_markup=keyboard
    )
    await callback.answer()

# Шаг 3: Обработчик нажатия кнопки "Заполнить анкету"
@dp.callback_query(F.data == "fill_form")
async def fill_form_callback(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id,
        "Отправляй всё <b><ins>ОДНИМ</ins></b> сообщением \n\nРасскажи нам о себе:\n"
        "1. Артистический псевдоним\n"
        "2. Кратко о себе <i>(как зовут; откуда ты; как давно занимаешься музыкой; на каких лейблах выпускаешься; играешь ли на вечеринках: если да, то на каких)</i>\n"
        "3. Прикрепи ссылку на свой Instagram\n"
        "4. Название трека\n"
        "5. Жанр трека\n"
        "6. Ссылка на твою карточку артиста в Яндекс музыке\n"
        "7. Твой ник в Telegram\n",
        parse_mode=ParseMode.HTML  # parse_mode добавлен
    )
    await state.set_state(DemoForm.waiting_for_profile_info) # Ждем информацию профиля (1-7)
    await callback.answer()

# Шаг 4: Обрабатываем информацию профиля (пункты 1-7)
@dp.message(DemoForm.waiting_for_profile_info)
async def process_profile_info(message: Message, state: FSMContext):
    try:
        await bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=message.chat.id, message_id=message.message_id)  # Пересылаем сообщение в чат админа
        await state.set_state(DemoForm.waiting_for_demo) # Переходим в состояние ожидания демки
        await message.reply("Отлично! \nТеперь прикрепи к сообщению демку в формате MP3 \n\n <i>ВАЖНО: \n 1. демки ссылками на облачное хранилище не принимаются \n 2. указанные в анкете название трека и артистический псевдоним должны совпадать с названием MP3-файла \n 3. если отправляешь две демки, они должны быть отправлены ОДНИМ сообщением</i>")
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")
        await message.reply("Произошла ошибка при пересылке сообщения. Попробуйте еще раз.")
        await state.clear() # Сбрасываем состояние

# Шаг 5: Обрабатываем демку (пункт 8)
@dp.message(DemoForm.waiting_for_demo, F.audio) # F.audio - более современный способ фильтрации аудио
async def process_demo(message: Message, state: FSMContext):
    try:
        await bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=message.chat.id, message_id=message.message_id)  # Пересылаем демку в чат админа

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить ещё одну демку", callback_data="send_demo")]
        ])
        await bot.send_message(message.chat.id,
            "Супер!\nАнкета и демка отправлены\n\nПослушаем и дадим обратную связь",
            reply_markup=keyboard, parse_mode=ParseMode.HTML  # Добавлен parse_mode
        )
        await state.clear()  # Сбрасываем состояние
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")
        await message.reply("Произошла ошибка при пересылке сообщения. Попробуйте еще раз.")
        await state.clear() # Сбрасываем состояние

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
        reply_markup=keyboard, parse_mode=ParseMode.HTML # Добавлен parse_mode
    )
    await callback.answer()

async def main():
    try:
        await dp.start_polling(bot, skip_updates=True)  # Добавлен skip_updates
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
