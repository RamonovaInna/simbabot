import aiosqlite

DB_NAME = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER,
            to_user_id INTEGER,
            text TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await db.commit()

async def add_user(telegram_id, name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (telegram_id, name) VALUES (?, ?)",
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
        cursor = await db.execute(
            "INSERT INTO tasks (from_user_id, to_user_id, text) VALUES (?, ?, ?)",
            (from_id, to_id, text),
        )
        await db.commit()
        return cursor.lastrowid

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

async def get_task_sender(task_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT from_user_id FROM tasks WHERE id = ?", (task_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
