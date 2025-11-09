# rootdir: manager/app/database/schema.py

from app.database.connection import Database
from app.config import QUERIES
from app.utils.logger import get_logger

logger = get_logger("schema")


async def init_schema(db: Database):
    """ساخت جداول دیتابیس"""
    await db.execute("create_users_table")
    await db.execute("create_sessions_table")
    await db.execute("create_messages_table")
    logger.info("Schema initialized")
