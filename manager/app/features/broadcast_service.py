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