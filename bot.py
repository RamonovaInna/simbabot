import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN") or "ваш_токен"  # Вставьте токен для теста
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class RequestStates(StatesGroup):
    waiting_for_recipient = State()

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    try:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Маша", callback_data="select_Маша")],
                [InlineKeyboardButton(text="Инна", callback_data="select_Инна")]
            ]
        )
        await message.answer(
            f"Привет, {message.from_user.first_name}! Я готов к бытовым подвигам 💪\n\nКому поручить задание?",
            reply_markup=keyboard
        )
        await state.set_state(RequestStates.waiting_for_recipient)
        logger.info(f"Sent keyboard and set state for user {message.from_user.id}")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        logger.error(f"Error in /start: {str(e)}")

@dp.message(Command("menu"))
async def open_menu(message: types.Message, state: FSMContext):
    try:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Маша", callback_data="select_Маша")],
                [InlineKeyboardButton(text="Инна", callback_data="select_Инна")]
            ]
        )
        await message.answer("Кому поручить задание?", reply_markup=keyboard)
        await state.set_state(RequestStates.waiting_for_recipient)
        logger.info(f"Sent menu keyboard for user {message.from_user.id}")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        logger.error(f"Error in /menu: {str(e)}")

@dp.message()
async def handle_text(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == RequestStates.waiting_for_recipient:
        await message.answer("Пожалуйста, выбери получателя, нажав на кнопку ⬆️")
    else:
        await message.answer("Используй /start или /menu, чтобы начать.")
    logger.info(f"Handled text message from user {message.from_user.id}: {message.text}")

async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)
    logger.info("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
