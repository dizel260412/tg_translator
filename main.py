from googletrans import Translator
from config import bot_token, countries
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType, Message, File
import sqlite3
from pathlib import Path

bot = Bot(token=bot_token)
dp = Dispatcher(bot)
inline_kb_full = InlineKeyboardMarkup(row_width=1)
inline_btn_1 = InlineKeyboardButton('🇷🇺 Россия (ru) 🇷🇺', callback_data='btn_1')
inline_btn_2 = InlineKeyboardButton('🏴󠁧󠁢󠁥󠁮󠁧󠁿 English (en) 🏴󠁧󠁢󠁥󠁮󠁧󠁿', callback_data='btn_2')
inline_btn_3 = InlineKeyboardButton('🇫🇷 French (fr) 🇫🇷', callback_data='btn_3')
inline_btn_4 = InlineKeyboardButton('🇩🇪 Deutsch (de) 🇩🇪', callback_data='btn_4')
inline_btn_5 = InlineKeyboardButton('🇪🇦 Spanish (es) 🇪🇦', callback_data='btn_5')
inline_kb_full.add(inline_btn_1, inline_btn_2, inline_btn_3, inline_btn_4, inline_btn_5)
l = []


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Запускаем бота с помощью /start"""

    start_buttons = ["Сменить языки", "О создателе"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    locale = message.from_user.locale
    tr_locate = 'en'

    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute(
        f'INSERT or IGNORE INTO users VALUES("{message.from_user.id}", "@{message.from_user.username}", "{locale}", "{tr_locate}")')
    conn.commit()
    cur.close()

    await message.answer("Привет, я бот переводчик!\nHi! I'm translator bot!", reply_markup=keyboard)
    await message.answer(
        f'Ваш язык: {locale}\nЯзык перевода: {tr_locate}\nДля смены языков нажмите кнопку - Сменить языки)')


@dp.message_handler(Text(equals="Сменить языки"))
async def _help_(message: types.Message):
    await message.answer("Язык на котором будем писать?", reply_markup=inline_kb_full)
    await message.answer("Язык на который будем переводить?", reply_markup=inline_kb_full)


@dp.callback_query_handler(Text(startswith='btn_'))
async def process_callback_kb1btn1(callback: types.CallbackQuery):
    code = int(callback.data.split('_')[1])
    l.append(code)
    if len(l) == 2 and l[0] != l[1]:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        sql_update_query = f'Update users set lang = "{countries.get(l[0]).get("cod")}" where user_id = "{callback.from_user.id}"'
        cur.execute(sql_update_query)
        sql_update_query1 = f'Update users set tr_lang = "{countries.get(l[1]).get("cod")}" where user_id = "{callback.from_user.id}"'
        cur.execute(sql_update_query1)
        conn.commit()
        cur.close()
        await callback.answer(f'Языки изменены на: {countries.get(l[0]).get("name")}'
                              f' {countries.get(l[0]).get("flag")} / '
                              f'{countries.get(l[1]).get("name")} '
                              f'{countries.get(l[1]).get("flag")} ')
        l.clear()


@dp.message_handler(Text(equals="О создателе"))
async def _help_(message: types.Message):
    tg = '@dnlteleshev'
    website = '#######'
    await message.answer(f'Telegram: {tg}\n'
                         f'Website: {website}')


@dp.message_handler()
async def translate(message: types.Message):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute(f"SELECT lang, tr_lang FROM users WHERE user_id = {message.from_user.id};")
    results = cur.fetchone()
    cur.execute(f'INSERT or IGNORE INTO words VALUES("{message.text.capitalize()}")')
    conn.commit()
    cur.close()

    translator = Translator()
    translation = translator.translate(text=message.text, src=str(results[0]), dest=str(results[1]))
    await message.reply(translation.text)


@dp.message_handler(content_types=[ContentType.VOICE])
async def voice_message_handler(message: Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, '123.mp3')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
