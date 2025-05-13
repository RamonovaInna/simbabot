import aiosqlite

DB_NAME = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        with open("schema.sql", "r") as f:
            await db.executescript(f.read())

async def add_user(telegram_id, name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, name) VALUES (?, ?)",
            (telegram_id, name),
        )
        await db.commit()

async def get_user_id_by_name(name):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT telegram_id FROM users WHERE name = ?", (name,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def save_task(from_id, to_id, text):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO tasks (from_user_id, to_user_id, text) VALUES (?, ?, ?)",
            (from_id, to_id, text),
        )
        await db.commit()
        return db.last_insert_rowid()

async def mark_task_status(task_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (status, task_id)
        )
        await db.commit()

async def get_task_text(task_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT text FROM tasks WHERE id = ?", (task_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
