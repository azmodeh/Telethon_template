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
