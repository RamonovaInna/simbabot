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
async def create_family(message: types.Message):
    await message.answer("🔧 Функция создания семьи будет доступна после обновления базы данных. Следующий шаг — внедрение семейного кода и ограничений внутри семьи.")

@dp.message(Command("присоединиться"))
async def join_family(message: types.Message):
    await message.answer("🔧 Функция присоединения к семье будет доступна после обновления базы данных. Ожидай код-приглашение от администратора семьи.")

@dp.message(Command("семья"))
async def show_family(message: types.Message):
    await message.answer("👨‍👩‍👧‍👦 Здесь позже появится список всех участников вашей семьи.")

@dp.message(Command("добавить_члена"))
async def register_member(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Формат: /добавить_члена [Имя]")
        return
    name = parts[1].strip()
    await add_user(message.from_user.id, name)
    await message.answer(f"Добавлен как {name} ✅")

@dp.message(Command("меню"))
async def open_menu(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Маша", callback_data="select_Маша")],
        [InlineKeyboardButton(text="Инна", callback_data="select_Инна")]
    ])
    await message.answer("Кому поручить задание?", reply_markup=keyboard)
    await state.set_state(RequestStates.waiting_for_recipient)

@dp.callback_query(RequestStates.waiting_for_recipient)
async def select_recipient(callback: types.CallbackQuery, state: FSMContext):
    name = callback.data.replace("select_", "")
    await state.update_data(recipient=name)

    # Предлагаем шаблоны или свой вариант
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚽 Операция \"Каловый барабашка\"", callback_data="task_toilet")],
        [InlineKeyboardButton(text="📦 Засада у двери (забери заказ)", callback_data="task_order")],
        [InlineKeyboardButton(text="🍴 Встревожь плиту (включи ужин)", callback_data="task_dinner")],
        [InlineKeyboardButton(text="🗑️ Миссия: вынос тела", callback_data="task_trash")],
        [InlineKeyboardButton(text="💧 Аква-доставка в миску", callback_data="task_water")],
        [InlineKeyboardButton(text="🔋 Порадуй розетку (поставь на зарядку)", callback_data="task_charge")],
        [InlineKeyboardButton(text="✍️ Написать вручную", callback_data="task_custom")]
    ])
    await callback.message.edit_text(f"Выбери поручение для {name}:", reply_markup=keyboard)
    await state.set_state(RequestStates.waiting_for_task_choice)

@dp.callback_query(RequestStates.waiting_for_task_choice)
async def handle_task_choice(callback: types.CallbackQuery, state: FSMContext):
    task_map = {
        "task_toilet": "Принести туалетную бумагу 🧻",
        "task_order": "Забрать заказ от двери 🍱",
        "task_dinner": "Поставить ужин на плиту 🍳",
        "task_trash": "Вынести мусор 🗑️",
        "task_water": "Налить воду в миску 💧",
        "task_charge": "Поставить телефон на зарядку 🔋"
    }

    task_code = callback.data
    if task_code == "task_custom":
        await callback.message.edit_text("Хорошо! Напиши своё задание текстом ✍️")
        await state.set_state(RequestStates.waiting_for_custom_text)
        return

    task_text = task_map.get(task_code, "")
    data = await state.get_data()
    to_name = data.get("recipient")
    to_id = await get_user_id_by_name(to_name)

    if not to_id:
        await callback.message.answer("Пользователь не найден в базе.")
        await state.clear()
        return

    task_id = await save_task(callback.from_user.id, to_id, task_text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done_{task_id}")],
        [InlineKeyboardButton(text="❌ Отказаться", callback_data=f"decline_{task_id}")]
    ])

    await bot.send_message(
        to_id,
        f"📬 <b>Новое поручение от {callback.from_user.first_name}:</b>\n\n<i>{task_text}</i>",
        reply_markup=kb
    )
    await callback.message.edit_text("Запрос отправлен! 📨")
    await state.clear()

@dp.message(RequestStates.waiting_for_custom_text)
async def get_task_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    to_name = data.get("recipient")
    task_text = message.text
    to_id = await get_user_id_by_name(to_name)

    if not to_id:
        await message.answer("Пользователь не найден в базе.")
        await state.clear()
        return

    task_id = await save_task(message.from_user.id, to_id, task_text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done_{task_id}")],
        [InlineKeyboardButton(text="❌ Отказаться", callback_data=f"decline_{task_id}")]
    ])

    await bot.send_message(
        to_id,
        f"📬 <b>Новое поручение от {message.from_user.first_name}:</b>\n\n<i>{task_text}</i>",
        reply_markup=kb
    )
    await message.answer("Запрос отправлен! 📨")
    await state.clear()

# ---------- КНОПКИ ЗАДАНИЯ ---------- #
@dp.callback_query(F.data.startswith("done_"))
async def mark_done(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    await mark_task_status(task_id, "done")
    text = await get_task_text(task_id)
    sender = await get_task_sender(task_id)
    await callback.message.edit_text(f"✅ Выполнено: {text}")
    await bot.send_message(sender, f"🎉 Задание выполнено: «{text}»")

@dp.callback_query(F.data.startswith("decline_"))
async def mark_declined(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    await mark_task_status(task_id, "declined")
    text = await get_task_text(task_id)
    sender = await get_task_sender(task_id)
    await callback.message.edit_text(f"❌ Задание отклонено: {text}")
    await bot.send_message(sender, f"😿 Задание отклонено: «{text}»")

# ---------- ЗАПУСК ---------- #
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
