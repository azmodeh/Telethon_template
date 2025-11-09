# ======================================================
# launcher.py - نقطه ورود اصلی
# ======================================================



# ======================================================
# app/main.py (MAX 4 خط)
# ======================================================


# ======================================================
# app/config/loader.py
# ======================================================



# ======================================================
# app/config/__init__.py
# ======================================================
from app.config.loader import (
    ENV,
    SETTINGS,
    MESSAGES,
    ERRORS,
    PATTERNS,
    QUERIES,
    COMMANDS,
    BASE,
    DATA
)


# ======================================================
# app/utils/logger.py
# ======================================================
import logging
from pathlib import Path
from app.config import DATA

LOGS = DATA / "logs"
LOGS.mkdir(exist_ok=True)


def get_logger(component: str) -> logging.Logger:
    """ساخت logger با فایل جداگانه برای هر کامپوننت"""
    logger = logging.getLogger(component)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        fh = logging.FileHandler(
            LOGS / f"{component}.log",
            encoding="utf-8"
        )
        fh.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        fmt = logging.Formatter(
            "%(asctime)s|%(name)s|%(levelname)s|%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger


# ======================================================
# app/database/connection.py
# ======================================================
import asyncpg
from typing import Optional
from app.config import ENV, QUERIES, MESSAGES, ERRORS
from app.utils.logger import get_logger

logger = get_logger("database")


class Database:
    """مدیریت اتصال PostgreSQL"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """اتصال به دیتابیس"""
        try:
            self.pool = await asyncpg.create_pool(
                host=ENV["db_host"],
                port=ENV["db_port"],
                user=ENV["db_user"],
                password=ENV["db_password"],
                database=ENV["db_name"],
                min_size=ENV["db_pool_min"],
                max_size=ENV["db_pool_max"]
            )
            logger.info(MESSAGES["db_connected"])
        except Exception as e:
            logger.error(ERRORS["db_connection_failed"])
            raise
    
    async def execute(self, query_key: str, *args):
        """اجرای کوئری"""
        query = QUERIES[query_key]
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query_key: str, *args):
        """دریافت رکوردها"""
        query = QUERIES[query_key]
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query_key: str, *args):
        """دریافت یک رکورد"""
        query = QUERIES[query_key]
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def close(self):
        """بستن اتصال"""
        if self.pool:
            await self.pool.close()
            logger.info(MESSAGES["db_closed"])


# ======================================================
# app/database/schema.py
# ======================================================
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


# ======================================================
# app/models/user.py
# ======================================================
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """مدل کاربر"""
    id: int
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_bot: bool
    is_premium: bool
    created_at: datetime
    updated_at: datetime


# ======================================================
# app/models/session.py
# ======================================================
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    """مدل نشست"""
    id: int
    user_id: int
    session_string: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ======================================================
# app/managers/bot_manager.py
# ======================================================
from telethon import TelegramClient, events
from app.config import ENV, MESSAGES, COMMANDS
from app.utils.logger import get_logger
from app.database.connection import Database

logger = get_logger("bot_manager")


class BotManager:
    """مدیریت ربات"""
    
    def __init__(self, db: Database):
        self.db = db
        self.client = TelegramClient(
            ENV["bot_session"],
            ENV["api_id"],
            ENV["api_hash"]
        )
    
    async def start(self):
        """شروع ربات"""
        await self.client.start(bot_token=ENV["bot_token"])
        logger.info(MESSAGES["bot_started"])
        self._register_handlers()
    
    def _register_handlers(self):
        """ثبت هندلرها"""
        self.client.add_event_handler(
            self._handle_start,
            events.NewMessage(pattern=COMMANDS["start"])
        )
        self.client.add_event_handler(
            self._handle_help,
            events.NewMessage(pattern=COMMANDS["help"])
        )
    
    async def _handle_start(self, event):
        """هندلر دستور start"""
        await event.respond(MESSAGES["welcome"])
        logger.info(f"Start: {event.sender_id}")
    
    async def _handle_help(self, event):
        """هندلر دستور help"""
        await event.respond(MESSAGES["help"])
        logger.info(f"Help: {event.sender_id}")
    
    async def stop(self):
        """توقف ربات"""
        await self.client.disconnect()
        logger.info(MESSAGES["bot_stopped"])


# ======================================================
# app/managers/userbot_manager.py
# ======================================================
from telethon import TelegramClient
from app.config import ENV, MESSAGES
from app.utils.logger import get_logger
from app.database.connection import Database

logger = get_logger("userbot_manager")


class UserbotManager:
    """مدیریت یوزربات"""
    
    def __init__(self, db: Database):
        self.db = db
        self.client = TelegramClient(
            ENV["userbot_session"],
            ENV["api_id"],
            ENV["api_hash"]
        )
    
    async def start(self):
        """شروع یوزربات"""
        await self.client.start(phone=ENV["userbot_phone"])
        logger.info(MESSAGES["userbot_started"])
    
    async def send_message(self, chat_id: int, text: str):
        """ارسال پیام"""
        try:
            await self.client.send_message(chat_id, text)
            logger.info(f"Message sent to {chat_id}")
        except Exception as e:
            logger.error(f"Send failed: {e}")
            raise
    
    async def stop(self):
        """توقف یوزربات"""
        await self.client.disconnect()
        logger.info(MESSAGES["userbot_stopped"])


# ======================================================
# app/features/user_service.py
# ======================================================
from app.database.connection import Database
from app.models.user import User
from app.config import MESSAGES, ERRORS
from app.utils.logger import get_logger

logger = get_logger("user_service")


class UserService:
    """سرویس مدیریت کاربران"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_user(self, user_data: dict) -> User:
        """ساخت کاربر"""
        await self.db.execute(
            "insert_user",
            user_data["user_id"],
            user_data.get("username"),
            user_data.get("first_name"),
            user_data.get("last_name"),
            user_data.get("phone"),
            user_data.get("is_bot", False),
            user_data.get("is_premium", False)
        )
        logger.info(MESSAGES["user_created"])
        return await self.get_user(user_data["user_id"])
    
    async def get_user(self, user_id: int):
        """دریافت کاربر"""
        row = await self.db.fetchrow("select_user", user_id)
        if not row:
            logger.error(ERRORS["user_not_found"])
            return None
        return User(**dict(row))
    
    async def update_user(self, user_id: int, data: dict):
        """به‌روزرسانی کاربر"""
        await self.db.execute(
            "update_user",
            data.get("username"),
            data.get("first_name"),
            user_id
        )
        logger.info(MESSAGES["user_updated"])


# ======================================================
# app/core/bootstrap.py
# ======================================================
import asyncio
from app.database.connection import Database
from app.database.schema import init_schema
from app.managers.bot_manager import BotManager
from app.managers.userbot_manager import UserbotManager
from app.config import MESSAGES
from app.utils.logger import get_logger

logger = get_logger("bootstrap")


async def initialize():
    """راه‌اندازی اولیه"""
    logger.info(MESSAGES["app_starting"])
    
    db = Database()
    await db.connect()
    await init_schema(db)
    
    bot = BotManager(db)
    userbot = UserbotManager(db)
    
    await bot.start()
    await userbot.start()
    
    logger.info(MESSAGES["app_started"])
    
    await asyncio.Event().wait()


def start():
    """نقطه شروع"""
    try:
        asyncio.run(initialize())
    except KeyboardInterrupt:
        logger.info(MESSAGES["app_stopped"])