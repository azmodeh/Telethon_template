# rootdir: manager/app/core/application.py
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

logger = get_logger("application")


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
