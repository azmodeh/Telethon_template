# rootdir: manager/app/managers/userbot_manager.py
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