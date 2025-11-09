# rootdir: manager/app/managers/bot_manager.py
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