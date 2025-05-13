import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.filters import Command
from database import init_db, add_user, get_user_id_by_name, save_task, mark_task_status, get_task_text

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f"Привет, {message.from_user.first_name}! Я готов к бытовым подвигам 💪")

@dp.message(Command("запрос"))
async def request_task(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Формат: /запрос [кому] [что сделать]")
        return
    to_name = args[1]
    task_text = args[2]

    to_id = await get_user_id_by_name(to_name)
    if not to_id:
        await message.answer("Пользователь с таким именем не найден.")
        return

    task_id = await save_task(message.from_user.id, to_id, task_text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done_{task_id}")],
        [InlineKeyboardButton(text="❌ Отказаться", callback_data=f"decline_{task_id}")],
    ])

    await bot.send_message(
        to_id,
        f"📬 <b>Новое поручение от {message.from_user.first_name}:</b>\n\n<i>{task_text}</i>",
        reply_markup=kb
    )
    await message.answer("Запрос отправлен!")

@dp.callback_query(F.data.startswith("done_"))
async def mark_done(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    await mark_task_status(task_id, "done")
    text = await get_task_text(task_id)
    await callback.message.edit_text(f"✅ Выполнено: {text}")

@dp.callback_query(F.data.startswith("decline_"))
async def mark_declined(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    await mark_task_status(task_id, "declined")
    text = await get_task_text(task_id)
    await callback.message.edit_text(f"❌ Отказ: {text}")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
