# ======================================================
# app/unit/validators.py
# ======================================================
import re
from app.config import PATTERNS, ERRORS
from app.utils.logger import get_logger

logger = get_logger("validators")


def validate_phone(phone: str) -> bool:
    """اعتبارسنجی شماره تلفن"""
    pattern = PATTERNS["phone_intl"]
    if not re.match(pattern, phone):
        logger.error(ERRORS["invalid_phone"])
        raise ValueError(ERRORS["invalid_phone"])
    return True


def validate_username(username: str) -> bool:
    """اعتبارسنجی نام کاربری"""
    pattern = PATTERNS["username"]
    if not re.match(pattern, username):
        logger.error(f"Invalid username: {username}")
        raise ValueError("Invalid username format")
    return True


def validate_chat_id(chat_id: str) -> bool:
    """اعتبارسنجی شناسه چت"""
    pattern = PATTERNS["chat_id"]
    if not re.match(pattern, str(chat_id)):
        logger.error(ERRORS["invalid_chat_id"])
        raise ValueError(ERRORS["invalid_chat_id"])
    return True


def validate_message_length(text: str, max_len: int) -> bool:
    """بررسی طول پیام"""
    if len(text) > max_len:
        logger.error(ERRORS["message_too_long"])
        raise ValueError(ERRORS["message_too_long"])
    return True


# ======================================================
# app/features/broadcast_service.py
# ======================================================
from typing import List
from app.database.connection import Database
from app.managers.bot_manager import BotManager
from app.config import MESSAGES, ERRORS, SETTINGS
from app.utils.logger import get_logger
from app.unit.validators import validate_message_length
import asyncio

logger = get_logger("broadcast_service")


class BroadcastService:
    """سرویس ارسال پیام گروهی"""
    
    def __init__(self, db: Database, bot: BotManager):
        self.db = db
        self.bot = bot
    
    async def get_all_users(self) -> List[int]:
        """دریافت لیست تمام کاربران"""
        rows = await self.db.fetch("select_all_users")
        return [row["user_id"] for row in rows]
    
    async def send_to_all(self, message: str) -> dict:
        """ارسال پیام به همه"""
        validate_message_length(
            message,
            SETTINGS["max_message_length"]
        )
        
        users = await self.get_all_users()
        success_count = 0
        fail_count = 0
        
        logger.info(f"Starting broadcast to {len(users)} users")
        
        for user_id in users:
            try:
                await self.bot.client.send_message(
                    user_id,
                    message
                )
                success_count += 1
                logger.debug(f"Sent to {user_id}")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                fail_count += 1
                logger.error(f"Failed for {user_id}: {e}")
        
        result = {
            "total": len(users),
            "success": success_count,
            "failed": fail_count
        }
        
        logger.info(f"Broadcast complete: {result}")
        return result


# ======================================================
# app/features/stats_service.py
# ======================================================
from app.database.connection import Database
from app.config import MESSAGES
from app.utils.logger import get_logger

logger = get_logger("stats_service")


class StatsService:
    """سرویس آمار"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_stats(self) -> dict:
        """دریافت آمار کلی"""
        total_users = await self.db.fetchrow("count_users")
        active_sessions = await self.db.fetchrow(
            "count_active_sessions"
        )
        
        stats = {
            "total_users": total_users["count"],
            "active_sessions": active_sessions["count"]
        }
        
        logger.info(f"Stats: {stats}")
        return stats


# ======================================================
# app/managers/session_manager.py
# ======================================================
from app.database.connection import Database
from app.models.session import Session
from app.config import MESSAGES, ERRORS
from app.utils.logger import get_logger

logger = get_logger("session_manager")


class SessionManager:
    """مدیریت نشست‌ها"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_session(
        self,
        user_id: int,
        session_string: str
    ) -> int:
        """ساخت نشست جدید"""
        await self.db.execute("deactivate_session", user_id)
        
        row = await self.db.fetchrow(
            "insert_session",
            user_id,
            session_string
        )
        
        session_id = row["id"]
        logger.info(MESSAGES["session_created"])
        return session_id
    
    async def get_active_session(self, user_id: int):
        """دریافت نشست فعال"""
        row = await self.db.fetchrow("select_session", user_id)
        
        if not row:
            logger.warning(ERRORS["session_not_found"])
            return None
        
        return Session(**dict(row))
    
    async def deactivate(self, user_id: int):
        """غیرفعال کردن نشست"""
        await self.db.execute("deactivate_session", user_id)
        logger.info(MESSAGES["session_expired"])


# ======================================================
# app/core/handlers.py
# ======================================================
from telethon import events
from app.managers.bot_manager import BotManager
from app.features.user_service import UserService
from app.features.stats_service import StatsService
from app.features.broadcast_service import BroadcastService
from app.config import MESSAGES, COMMANDS
from app.utils.logger import get_logger

logger = get_logger("handlers")


def register_all_handlers(
    bot: BotManager,
    user_service: UserService,
    stats_service: StatsService,
    broadcast_service: BroadcastService
):
    """ثبت تمام هندلرها"""
    
    @bot.client.on(events.NewMessage(pattern=COMMANDS["start"]))
    async def handle_start(event):
        """هندلر /start"""
        user_data = {
            "user_id": event.sender_id,
            "username": event.sender.username,
            "first_name": event.sender.first_name,
            "last_name": event.sender.last_name
        }
        
        await user_service.create_user(user_data)
        await event.respond(MESSAGES["welcome"])
        logger.info(f"Start: {event.sender_id}")
    
    @bot.client.on(events.NewMessage(pattern=COMMANDS["stats"]))
    async def handle_stats(event):
        """هندلر /stats"""
        stats = await stats_service.get_stats()
        
        text = f"📊 آمار:\n"
        text += f"کاربران: {stats['total_users']}\n"
        text += f"نشست‌های فعال: {stats['active_sessions']}"
        
        await event.respond(text)
        logger.info(f"Stats: {event.sender_id}")
    
    @bot.client.on(events.NewMessage(pattern=COMMANDS["help"]))
    async def handle_help(event):
        """هندلر /help"""
        await event.respond(MESSAGES["help"])
        logger.info(f"Help: {event.sender_id}")
    
    logger.info("All handlers registered")


# ======================================================
# app/core/bootstrap.py (نسخه کامل)
# ======================================================
import asyncio
from app.database.connection import Database
from app.database.schema import init_schema
from app.managers.bot_manager import BotManager
from app.managers.userbot_manager import UserbotManager
from app.managers.session_manager import SessionManager
from app.features.user_service import UserService
from app.features.stats_service import StatsService
from app.features.broadcast_service import BroadcastService
from app.core.handlers import register_all_handlers
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
    
    user_service = UserService(db)
    stats_service = StatsService(db)
    broadcast_service = BroadcastService(db, bot)
    
    await bot.start()
    await userbot.start()
    
    register_all_handlers(
        bot,
        user_service,
        stats_service,
        broadcast_service
    )
    
    logger.info(MESSAGES["app_started"])
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info(MESSAGES["app_stopped"])
        await bot.stop()
        await userbot.stop()
        await db.close()


def start():
    """نقطه شروع"""
    try:
        asyncio.run(initialize())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
