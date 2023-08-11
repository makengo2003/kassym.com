import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.types import ContentType, Message


logging.basicConfig(level=logging.INFO)
bot = Bot(token='6454586115:AAG9og9TP0yxSefacJ-jiFolCGqyxxwrOx0', parse_mode='HTML')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def welcome(msg: Message):
    await msg.answer(f"Ваш Chat Id: {msg.chat.id}")


@dp.message_handler(content_types=ContentType.TEXT)
async def get_message(msg: Message):
    await msg.answer(f"Ваш Chat Id: {msg.chat.id}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
