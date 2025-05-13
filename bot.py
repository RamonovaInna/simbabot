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

from database import (
    init_db,
    add_user,
    get_user_id_by_name,
    save_task,
    mark_task_status,
    get_task_text,
    get_task_sender,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ---------- FSM ---------- #
class RequestStates(StatesGroup):
    waiting_for_recipient = State()
    waiting_for_task_choice = State()
    waiting_for_custom_text = State()

# ---------- КОМАНДЫ ---------- #
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    try:
        await add_user(message.from_user.id, message.from_user.first_name)
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
        logger.info(f"Set state to waiting_for_recipient for user {message.from_user.id}")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        logger.error(f"Error in /start: {str(e)}")

# ... (остальные команды и обработчики без изменений) ...

# ---------- ЗАПУСК ---------- #
async def main():
    logger.info("Starting bot...")
    await init_db()
    await dp.start_polling(bot)
    logger.info("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
