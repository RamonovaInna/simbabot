import aiosqlite
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def init_db():
    try:
        async with aiosqlite.connect("simba.db") as db:
            with open("schema.sql", "r") as f:
                await db.executescript(f.read())
            await db.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

async def add_user(telegram_id: int, name: str):
    try:
        async with aiosqlite.connect("simba.db") as db:
            await db.execute("INSERT OR REPLACE INTO users (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
            await db.commit()
            logger.info(f"User {telegram_id} added with name {name}")
    except Exception as e:
        logger.error(f"Error adding user {telegram_id}: {str(e)}")

async def get_user_id_by_name(name: str) -> int:
    try:
        async with aiosqlite.connect("simba.db") as db:
            async with db.execute("SELECT telegram_id FROM users WHERE name = ?", (name,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting user ID for name {name}: {str(e)}")
        return None

async def save_task(from_user_id: int, to_user_id: int, text: str) -> int:
    try:
        async with aiosqlite.connect("simba.db") as db:
            result = await db.execute(
                "INSERT INTO tasks (from_user_id, to_user_id, text) VALUES (?, ?, ?)",
                (from_user_id, to_user_id, text)
            )
            await db.commit()
            task_id = result.lastrowid
            logger.info(f"Task {task_id} saved from {from_user_id} to {to_user_id}")
            return task_id
    except Exception as e:
        logger.error(f"Error saving task: {str(e)}")
        return None

async def mark_task_status(task_id: int, status: str):
    try:
        async with aiosqlite.connect("simba.db") as db:
            await db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            await db.commit()
            logger.info(f"Task {task_id} marked as {status}")
    except Exception as e:
        logger.error(f"Error marking task {task_id} status: {str(e)}")

async def get_task_text(task_id: int) -> str:
    try:
        async with aiosqlite.connect("simba.db") as db:
            async with db.execute("SELECT text FROM tasks WHERE id = ?", (task_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting task text for task {task_id}: {str(e)}")
        return None

async def get_task_sender(task_id: int) -> int:
    try:
        async with aiosqlite.connect("simba.db") as db:
            async with db.execute("SELECT from_user_id FROM tasks WHERE id = ?", (task_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting task sender for task {task_id}: {str(e)}")
        return None
