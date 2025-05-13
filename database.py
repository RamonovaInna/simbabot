import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.filters import Command

from database import (
    init_db,
    add_user,
    get_user_id_by_name,
    save_task,
    mark_task_status,
    get_task_text,
    get_task_sender,
    create_family,
    assign_user_to_family,
    get_family_id_by_code,
    get_family_members,
    get_user_family_id
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ---------- FSM ---------- #
class RequestStates(StatesGroup):
    waiting_for_recipient = State()
    waiting_for_task_choice = State()
    waiting_for_custom_text = State()

# ---------- КОМАНДЫ ---------- #
@dp.message(Command("start"))
async def start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f"Привет, {message.from_user.first_name}! Я готов к бытовым подвигам 💪")

@dp.message(Command("создать_семью"))
async def create_family_cmd(message: types.Message):
    user_name = message.from_user.first_name
    family_id, code = await create_family(f"Семья {user_name}")
    await assign_user_to_family(message.from_user.id, family_id)
    await message.answer(f"🎉 Семья создана!
Код приглашения: <code>{code}</code>")

@dp.message(Command("присоединиться"))
async def join_family_cmd(message: types.Message):
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Формат команды: /присоединиться ABC123")
        return
    code = parts[1].strip().upper()
    family_id = await get_family_id_by_code(code)
    if not family_id:
        await message.answer("❌ Семья с таким кодом не найдена.")
        return
    await assign_user_to_family(message.from_user.id, family_id)
    await message.answer("✅ Вы присоединились к семье!")

@dp.message(Command("семья"))
async def show_family(message: types.Message):
    family_id = await get_user_family_id(message.from_user.id)
    if not family_id:
        await message.answer("😕 Вы пока не в семье. Создайте или присоединитесь.")
        return
    members = await get_family_members(family_id)
    await message.answer("👨‍👩‍👧‍👦 Ваша семья:\n" + "\n".join(f"• {name}" for name in members))
